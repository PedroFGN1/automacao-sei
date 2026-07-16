import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
# pyrefly: ignore [missing-import]
import pypdf
from app.core.plugin_base import BasePlugin

class IndexadorPdfPlugin(BasePlugin):
    """
    Plugin para extrair texto de arquivos PDF de processos do SEI,
    armazenar no banco SQLite e realizar buscas rápidas por palavras-chave.
    """
    @property
    def id(self) -> str:
        return "indexador_pdf"

    @property
    def name(self) -> str:
        return "Indexador e Buscador de PDFs"

    @property
    def description(self) -> str:
        return "Varre uma pasta de PDFs, extrai o texto estruturado para o banco de dados e permite buscar por palavras-chave."

    def get_params_schema(self) -> List[Dict[str, Any]]:
        default_db = r"C:\Users\pedro.galvao\Documents\automacao.db"
        default_dir = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes"
        
        return [
            {
                "name": "db_file",
                "label": "Caminho do Banco SQLite (automacao.db)",
                "type": "file",
                "is_required": True,
                "default_value": default_db,
                "allowed_extensions": [".db", ".sqlite"]
            },
            {
                "name": "diretorio_pdfs",
                "label": "Diretório de PDFs a Indexar",
                "type": "directory",
                "is_required": True,
                "default_value": default_dir
            },
            {
                "name": "termo_busca",
                "label": "Termo de Busca Rápida (Opcional - se fornecido, faz apenas a busca)",
                "type": "text",
                "is_required": False
            }
        ]

    def inicializar_banco(self, db_file: str):
        """Inicializa as tabelas necessárias no banco SQLite."""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Cria a tabela de processos (pai) caso não exista (mecanismo de resiliência)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processos (
                numero_processo TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                tentativas INTEGER DEFAULT 0,
                ultima_execucao TEXT,
                mensagem_erro TEXT,
                prazo TEXT
            )
        """)
        
        # Cria a tabela de processos_texto se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processos_texto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_processo TEXT NOT NULL,
                texto_completo TEXT,
                data_processamento TEXT NOT NULL,
                FOREIGN KEY (numero_processo) REFERENCES processos (numero_processo) ON DELETE CASCADE
            );
        """)
        
        # Cria índice
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_processos_texto_numero 
            ON processos_texto (numero_processo);
        """)
        conn.commit()
        conn.close()

    def garantir_processo_no_banco(self, db_file: str, numero_processo: str):
        """Garante que o processo existe na tabela principal para Foreign Key."""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processos WHERE numero_processo = ?", (numero_processo,))
        if not cursor.fetchone():
            timestamp_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO processos (numero_processo, status, tentativas, ultima_execucao)
                VALUES (?, 'BAIXADO', 1, ?)
            """, (numero_processo, timestamp_atual))
            conn.commit()
        conn.close()

    def extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Extrai o texto de um PDF de forma sequencial página por página."""
        texto_paginas = []
        with open(caminho_pdf, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for pagina in reader.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_paginas.append(texto_extraido)
                    
        texto_completo = "\n".join(texto_paginas).strip()
        if not texto_completo:
            return "[PDF_DIGITALIZADO_SEM_TEXTO_NATIVO]"
        return texto_completo

    def executar_indexacao(self, db_file: str, pasta_pdfs: str, logger: Any):
        """Varre e indexa todos os arquivos PDF da pasta."""
        if not os.path.exists(pasta_pdfs):
            raise FileNotFoundError(f"O diretório '{pasta_pdfs}' não existe.")
            
        arquivos = os.listdir(pasta_pdfs)
        padrao_sei = re.compile(r"^(?:SEI_)?(\d+)\.pdf$", re.IGNORECASE)
        
        pdfs_para_processar = []
        for arq in arquivos:
            match = padrao_sei.match(arq)
            if match:
                numero_processo = match.group(1)
                caminho_completo = os.path.join(pasta_pdfs, arq)
                pdfs_para_processar.append((numero_processo, caminho_completo))
                
        total = len(pdfs_para_processar)
        if total == 0:
            logger(f"Nenhum PDF no padrão 'SEI_numero.pdf' ou 'numero.pdf' foi encontrado em '{pasta_pdfs}'.", "WARNING")
            return
            
        logger(f"Iniciando indexação de {total} arquivos PDF...", "INFO")
        
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        sucessos = 0
        ignorados = 0
        falhas = 0
        
        for idx, (num_proc, caminho_pdf) in enumerate(pdfs_para_processar, 1):
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM processos_texto WHERE numero_processo = ?", (num_proc,))
                
                if cursor.fetchone():
                    logger(f"[{idx}/{total}] Processo {num_proc} - Ignorado (Já Indexado)", "INFO")
                    ignorados += 1
                    continue
                    
                self.garantir_processo_no_banco(db_file, num_proc)
                texto = self.extrair_texto_pdf(caminho_pdf)
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO processos_texto (numero_processo, texto_completo, data_processamento)
                    VALUES (?, ?, ?)
                """, (num_proc, texto, timestamp))
                conn.commit()
                
                logger(f"[{idx}/{total}] Processo {num_proc} - Indexado com sucesso", "INFO")
                sucessos += 1
            except Exception as e:
                logger(f"[{idx}/{total}] Processo {num_proc} - Falha ao indexar: {str(e)}", "ERROR")
                falhas += 1
                
        conn.close()
        logger(f"Indexação concluída. Sucessos: {sucessos}, Ignorados: {ignorados}, Falhas: {falhas}.", "INFO")

    def executar_busca(self, db_file: str, termo: str, logger: Any):
        """Busca o termo informado no banco SQLite indexado."""
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Banco de dados '{db_file}' não encontrado. Realize a indexação primeiro.")
            
        logger(f"Buscando no banco indexado por: '{termo}'...", "INFO")
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        query = "SELECT numero_processo, texto_completo FROM processos_texto WHERE texto_completo LIKE ?"
        cursor.execute(query, (f"%{termo}%",))
        resultados = cursor.fetchall()
        
        if not resultados:
            logger(f"Nenhuma ocorrência do termo '{termo}' foi encontrada no banco.", "WARNING")
            conn.close()
            return
            
        logger(f"Encontrado(s) {len(resultados)} processo(s) correspondente(s):", "INFO")
        
        for num_proc, texto in resultados:
            logger(f"Processo: {num_proc}", "INFO")
            
            # Destaca trecho onde o termo ocorre
            match = re.search(re.escape(termo), texto, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 60)
                end = min(len(texto), match.end() + 60)
                trecho = texto[start:end].replace("\n", " ").strip()
                logger(f"  Trecho: ... {trecho} ...", "INFO")
            else:
                logger("  Trecho: [Texto indisponível para exibição parcial]", "INFO")
                
        conn.close()

    def execute(self, params: Dict[str, Any], logger: Any) -> Dict[str, Any]:
        db_file = params["db_file"]
        pasta_pdfs = params["diretorio_pdfs"]
        termo = params.get("termo_busca", "").strip()
        
        self.inicializar_banco(db_file)
        
        if termo:
            self.executar_busca(db_file, termo, logger)
            return {"status": "busca_concluida", "termo": termo}
        else:
            self.executar_indexacao(db_file, pasta_pdfs, logger)
            return {"status": "indexacao_concluida"}
        
        return {"status": "ok"}
