import sqlite3
import os
from datetime import datetime

DB_FILE = "automacao.db"

def obter_conexao():
    """
    Retorna uma conexão ativa com o banco de dados SQLite local.
    """
    return sqlite3.connect(DB_FILE)

def inicializar_banco():
    """
    Cria a tabela 'processos' caso ela não exista no banco de dados.
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                status TEXT NOT NULL,
                detalhes TEXT,
                data_criacao TEXT NOT NULL,
                data_atualizacao TEXT NOT NULL
            )
        """)
        conn.commit()

# Inicializa o banco de dados automaticamente ao importar o módulo
inicializar_banco()

def salvar_processo(numero: str, tipo: str, status: str, detalhes: str = None) -> bool:
    """
    Insere um novo processo ou atualiza um processo existente se o número for idêntico.
    """
    agora = datetime.now().isoformat()
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processos WHERE numero = ?", (numero,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("""
                UPDATE processos 
                SET status = ?, detalhes = ?, data_atualizacao = ? 
                WHERE numero = ?
            """, (status, detalhes, agora, numero))
        else:
            cursor.execute("""
                INSERT INTO processos (numero, tipo, status, detalhes, data_criacao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (numero, tipo, status, detalhes, agora, agora))
        conn.commit()
    return True

def obter_processos_paginados(pagina: int, itens_por_pagina: int, filtro_status: str = None, busca: str = None) -> list:
    """
    Retorna a lista de processos de forma paginada baseada em filtros e busca.
    """
    offset = (pagina - 1) * itens_por_pagina
    query = "SELECT id, numero, tipo, status, detalhes, data_criacao, data_atualizacao FROM processos WHERE 1=1"
    params = []
    
    if filtro_status:
        query += " AND status = ?"
        params.append(filtro_status)
        
    if busca:
        query += " AND (numero LIKE ? OR tipo LIKE ?)"
        busca_wildcard = f"%{busca}%"
        params.extend([busca_wildcard, busca_wildcard])
        
    query += " ORDER BY data_atualizacao DESC LIMIT ? OFFSET ?"
    params.extend([itens_por_pagina, offset])
    
    with obter_conexao() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def obter_total_processos(filtro_status: str = None, busca: str = None) -> int:
    """
    Retorna a quantidade total de processos correspondentes aos filtros.
    """
    query = "SELECT COUNT(*) FROM processos WHERE 1=1"
    params = []
    
    if filtro_status:
        query += " AND status = ?"
        params.append(filtro_status)
        
    if busca:
        query += " AND (numero LIKE ? OR tipo LIKE ?)"
        busca_wildcard = f"%{busca}%"
        params.extend([busca_wildcard, busca_wildcard])
        
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        return total

def carregar_sementes():
    """
    Popula o banco com alguns dados fictícios se estiver vazio.
    """
    if obter_total_processos() == 0:
        processos_teste = [
            ("52100.003412/2026-11", "Licenciamento Ambiental", "PENDENTE", None),
            ("52100.003413/2026-22", "Outorga de Direito de Uso", "PROCESSADO", "Exportado com sucesso para planilha Rede"),
            ("52100.003414/2026-33", "Fiscalização de Emissões", "ERRO", "Falha de rede ao conectar no SEI: Timeout"),
            ("52100.003415/2026-44", "Auto de Infração", "PENDENTE", None),
            ("52100.003416/2026-55", "Defesa Prévia", "PROCESSANDO", "Processando arquivo PDF: peticao.pdf"),
            ("52100.003417/2026-66", "Recurso Administrativo", "PENDENTE", None),
            ("52100.003418/2026-77", "Termo de Ajuste de Conduta", "PROCESSADO", "Concluído via n8n IA"),
            ("52100.003419/2026-88", "Relatório de Vistoria", "ERRO", "Erro de OCR no PDF digitalizado"),
            ("52100.003420/2026-99", "Análise de Projeto", "PENDENTE", None),
            ("52100.003421/2026-00", "Parecer Técnico", "PENDENTE", None),
            ("52100.003422/2026-10", "Solicitação de Certidão", "PENDENTE", None),
            ("52100.003423/2026-20", "Vistoria Técnica", "PENDENTE", None),
        ]
        for numero, tipo, status, detalhes in processos_teste:
            salvar_processo(numero, tipo, status, detalhes)

# Carrega os dados fictícios iniciais
carregar_sementes()

