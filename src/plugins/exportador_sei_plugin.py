import os
import sys
import time
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from playwright.sync_api import sync_playwright
from src.core.plugin_base import BasePlugin

class ExportadorSeiPlugin(BasePlugin):
    """
    Plugin para exportar processos do SEI em PDF, conectando-se a uma sessão
    do Chrome aberta via protocolo CDP na porta 9222.
    """
    @property
    def id(self) -> str:
        return "exportador_sei"

    @property
    def name(self) -> str:
        return "Exportador de Processos SEI"

    @property
    def description(self) -> str:
        return "Conecta ao Chrome (porta 9222), extrai e baixa processos do SEI em formato PDF e identifica prazos."

    def get_params_schema(self) -> List[Dict[str, Any]]:
        default_db = r"C:\Users\pedro.galvao\Documents\automacao.db"
        default_export = r"C:\SEI_Exportacoes"
        default_txt = r"processos.txt"
        
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
                "name": "export_dir",
                "label": "Diretório de Destino dos PDFs",
                "type": "directory",
                "is_required": True,
                "default_value": default_export
            },
            {
                "name": "lista_processos",
                "label": "Números de Processos (separados por vírgula ou espaço)",
                "type": "text",
                "is_required": False
            },
            {
                "name": "planilha_entrada",
                "label": "Ou arquivo processos.txt",
                "type": "file",
                "is_required": False,
                "default_value": default_txt,
                "allowed_extensions": [".txt"]
            },
            {
                "name": "delay_processos",
                "label": "Intervalo entre Processos (segundos)",
                "type": "text",
                "is_required": True,
                "default_value": "4"
            }
        ]

    # === HELPERS DO BANCO DE DADOS ===
    def inicializar_banco(self, db_file: str, processos: List[str], logger: Any):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
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
        conn.commit()
        
        try:
            cursor.execute("ALTER TABLE processos ADD COLUMN prazo TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
            
        cursor.execute("SELECT numero_processo FROM processos")
        processos_no_db = {row[0] for row in cursor.fetchall()}
        
        processos_unicos = list(dict.fromkeys(processos))
        novos = [(p, "PENDENTE") for p in processos_unicos if p not in processos_no_db]
        
        if novos:
            cursor.executemany("INSERT OR IGNORE INTO processos (numero_processo, status) VALUES (?, ?)", novos)
            conn.commit()
            logger(f"Sincronizados {len(novos)} novos processos no banco de dados.", "INFO")
            
        conn.close()

    def obter_processos_a_executar(self, db_file: str, processos_txt: List[str]) -> List[str]:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT numero_processo FROM processos WHERE status = 'SUCESSO'")
        sucessos = {row[0] for row in cursor.fetchall()}
        conn.close()
        return [p for p in processos_txt if p not in sucessos]

    def atualizar_status_processo(self, db_file: str, numero_processo: str, status: str, mensagem_erro: str = None, incrementar_tentativa: bool = False, prazo: str = None):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        set_clause = "status = ?, ultima_execucao = ?, mensagem_erro = ?"
        params = [status, agora, mensagem_erro]
        
        if prazo is not None:
            set_clause += ", prazo = ?"
            params.append(prazo)
            
        if incrementar_tentativa:
            set_clause += ", tentativas = tentativas + 1"
            
        params.append(numero_processo)
        query = f"UPDATE processos SET {set_clause} WHERE numero_processo = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    # === HELPERS DO PLAYWRIGHT ===
    def obter_pagina_sei(self, browser, logger):
        contexts = browser.contexts
        context = contexts[0] if contexts else browser.new_context()
        pages = context.pages
        
        for p in pages:
            try:
                url = p.url.lower()
                title = p.title().lower()
                if "sei" in url or "sistema eletrônico de informações" in title or "controle_processos" in url:
                    logger(f"Aba do SEI detectada: '{p.title()}' (URL: {p.url})", "INFO")
                    return p, context
            except Exception:
                continue
                
        if pages:
            logger(f"Nenhuma aba identificada por URL. Usando primeira aba aberta: '{pages[0].title()}'", "INFO")
            return pages[0], context
        else:
            logger("Nenhuma aba aberta. Criando nova página...", "INFO")
            return context.new_page(), context

    def preencher_busca_rapida(self, page, numero_processo) -> bool:
        selectors = [
            "#txtPesquisaRapida",
            "input[name='txtPesquisaRapida']",
            "input[placeholder*='Pesquisa']"
        ]
        for sel in selectors:
            try:
                loc = page.locator(sel)
                if loc.first.is_visible():
                    loc.first.fill("")
                    loc.first.fill(numero_processo)
                    loc.first.press("Enter")
                    return True
            except Exception:
                pass
        for frame in page.frames:
            for sel in selectors:
                try:
                    loc = frame.locator(sel)
                    if loc.first.is_visible():
                        loc.first.fill("")
                        loc.first.fill(numero_processo)
                        loc.first.press("Enter")
                        return True
                except Exception:
                    pass
        return False

    def encontrar_botao_gerar_pdf(self, page):
        selectors = [
            "a[href*='acao=procedimento_gerar_pdf']",
            "a[onclick*='acao=procedimento_gerar_pdf']",
            "a:has(img[src*='processo_gerar_pdf'])",
            "img[src*='processo_gerar_pdf']",
            "a[title*='Gerar Arquivo PDF']",
            "a[title*='Gerar PDF']",
            "a[title*='PDF']"
        ]
        try:
            frame_conteudo = page.frame_locator("#ifrConteudoVisualizacao")
            for sel in selectors:
                loc = frame_conteudo.locator(sel)
                if loc.first.is_visible():
                    return loc.first
        except Exception:
            pass
        try:
            frame_visualizacao = page.frame_locator("#ifrVisualizacao")
            for sel in selectors:
                loc = frame_visualizacao.locator(sel)
                if loc.first.is_visible():
                    return loc.first
        except Exception:
            pass
        for sel in selectors:
            try:
                loc = page.locator(sel)
                if loc.first.is_visible():
                    return loc.first
            except Exception:
                pass
        return None

    def clicar_no_raiz_arvore(self, page, numero_processo) -> bool:
        frame_arvore = None
        for f in page.frames:
            if f.name == "ifrArvore" or "ifrArvore" in f.url:
                frame_arvore = f
                break
        if not frame_arvore:
            try:
                frame_arvore = page.frame_locator("#ifrArvore")
            except Exception:
                pass
        if frame_arvore:
            clean_proc = "".join(filter(str.isdigit, numero_processo))
            candidates = [
                f"a:has-text('{numero_processo}')",
                f"a:has-text('{clean_proc}')",
                "a[href*='procedimento_visualizar']",
                "a[id^='anchor']"
            ]
            for c in candidates:
                try:
                    loc = frame_arvore.locator(c)
                    if loc.first.is_visible():
                        loc.first.click()
                        return True
                except Exception:
                    pass
        return False

    def extrair_prazo_processo(self, page) -> str:
        frame_arvore = None
        for f in page.frames:
            if f.name == "ifrArvore" or "ifrArvore" in f.url:
                frame_arvore = f
                break
        if not frame_arvore:
            try:
                frame_arvore = page.frame_locator("#ifrArvore")
            except Exception:
                pass
        if not frame_arvore:
            return None
            
        selectors = [
            "img[id^='iconCP']",
            "img[src*='controle_prazo']",
            "a[href*='controle_prazo_definir'] img"
        ]
        for sel in selectors:
            try:
                loc = frame_arvore.locator(sel)
                if loc.first.is_visible(timeout=1000):
                    title = loc.first.get_attribute("title")
                    if title:
                        return " ".join(title.split())
            except Exception:
                pass
        return None

    def configurar_e_gerar_pdf(self, page, context, numero_processo, export_dir):
        frame = None
        try:
            frame = page.frame_locator("#ifrConteudoVisualizacao").frame_locator("#ifrVisualizacao")
        except Exception:
            pass
        if not frame:
            frame = page.frame_locator("#ifrVisualizacao")
            
        submit_selectors = [
            "button[name='btnGerar']",
            "#btnGerar",
            "input[name='btnGerar']",
            "button:has-text('Gerar')"
        ]
        submit_button = None
        for sel in submit_selectors:
            try:
                loc = frame.locator(sel)
                loc.first.wait_for(state="visible", timeout=10000)
                submit_button = loc.first
                break
            except Exception:
                pass
        if not submit_button:
            raise Exception("Botão 'Gerar' não encontrado.")

        # Seleciona "Todos os documentos" (T)
        radio_selectors = [
            "input[value='T']",
            "input[name='rdoTipo'][value='T']",
            "#rdoDocumentoTodos"
        ]
        for sel in radio_selectors:
            try:
                loc = frame.locator(sel)
                if loc.first.is_visible():
                    loc.first.check()
                    break
            except Exception:
                pass

        with page.expect_download(timeout=60000) as download_info:
            submit_button.click()
            
        download = download_info.value
        os.makedirs(export_dir, exist_ok=True)
        download_path = os.path.join(export_dir, f"{numero_processo}.pdf")
        download.save_as(download_path)

    def verificar_pdf_valido(self, numero_processo, export_dir) -> bool:
        pdf_path = os.path.join(export_dir, f"{numero_processo}.pdf")
        if os.path.exists(pdf_path):
            return os.path.getsize(pdf_path) > 1024
        return False

    # === EXECUÇÃO ===
    def execute(self, params: Dict[str, Any], logger: Any) -> Dict[str, Any]:
        db_file = params["db_file"]
        export_dir = params["export_dir"]
        delay = int(params["delay_processos"])
        
        # 1. Carrega lista de processos
        processos = []
        raw_proc = params.get("lista_processos", "").strip()
        if raw_proc:
            processos = [p.strip() for p in raw_proc.replace(",", " ").split() if p.strip()]
            
        if not processos:
            planilha_path = params.get("planilha_entrada", "").strip()
            if planilha_path and os.path.exists(planilha_path):
                with open(planilha_path, "r", encoding="utf-8") as f:
                    for line in f:
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith("#"):
                            processos.append(clean_line)
                            
        # Deduplica
        processos = list(dict.fromkeys(processos))
        
        if not processos:
            raise ValueError("Nenhum número de processo foi fornecido via parâmetros ou planilha.")
            
        logger(f"Processos carregados no lote: {len(processos)}", "INFO")
        
        # Sincroniza e obtém fila pendente
        self.inicializar_banco(db_file, processos, logger)
        fila = self.obter_processos_a_executar(db_file, processos)
        total = len(fila)
        
        logger(f"Processos pendentes a exportar: {total}/{len(processos)}", "INFO")
        if total == 0:
            logger("Todos os processos da lista já foram concluídos com sucesso anteriormente.", "INFO")
            return {"status": "sem_pendencias", "total": len(processos)}
            
        os.makedirs(export_dir, exist_ok=True)
        
        chrome_url = "http://localhost:9222"
        logger(f"Conectando ao Chrome CDP em {chrome_url}...", "INFO")
        
        sucessos = 0
        falhas = 0
        ignorados = 0
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(chrome_url)
            except Exception as e:
                raise ConnectionError(f"Não foi possível conectar ao Chrome na porta 9222. Verifique se iniciar_chrome_debug.bat está rodando. Detalhes: {str(e)}")
                
            try:
                page, context = self.obter_pagina_sei(browser, logger)
                page.set_default_timeout(15000)
                url_base = page.url
                
                for idx, num_proc in enumerate(fila, 1):
                    logger(f"[{idx}/{total}] Processando processo: {num_proc}...", "INFO")
                    
                    if self.verificar_pdf_valido(num_proc, export_dir):
                        self.atualizar_status_processo(db_file, num_proc, "SUCESSO")
                        logger(f"  Processo {num_proc} já possui PDF exportado. Ignorado.", "INFO")
                        ignorados += 1
                        continue
                        
                    tentativa = 1
                    limite_tentativas = 2
                    sucesso_proc = False
                    ultimo_erro = ""
                    prazo = None
                    
                    while tentativa <= limite_tentativas and not sucesso_proc:
                        try:
                            # 1. Busca
                            if not self.preencher_busca_rapida(page, num_proc):
                                page.reload()
                                page.wait_for_load_state("load")
                                time.sleep(2)
                                if not self.preencher_busca_rapida(page, num_proc):
                                    raise Exception("Campo de busca rápida não encontrado.")
                                    
                            # 2. Aguarda carregamento
                            try:
                                page.wait_for_selector("#ifrConteudoVisualizacao", timeout=15000)
                            except Exception:
                                alert_selectors = [".infraMensagem", ".mensagem", "#mensagem", "text='não encontrado'", "text='inexistente'"]
                                alert_text = ""
                                for sel in alert_selectors:
                                    loc = page.locator(sel)
                                    if loc.is_visible():
                                        alert_text = loc.inner_text().strip()
                                        break
                                if alert_text:
                                    raise Exception(f"Erro SEI: {alert_text}")
                                raise Exception("Timeout aguardando visualização do processo.")
                                
                            time.sleep(2.5)
                            
                            # 3. Prazo
                            try:
                                prazo = self.extrair_prazo_processo(page)
                                if prazo:
                                    logger(f"  Prazo identificado: {prazo}", "INFO")
                            except Exception as pe:
                                logger(f"  Aviso ao ler prazo: {str(pe)}", "WARNING")
                                
                            # 4. Botão PDF
                            pdf_btn = self.encontrar_botao_gerar_pdf(page)
                            if not pdf_btn:
                                self.clicar_no_raiz_arvore(page, num_proc)
                                time.sleep(2)
                                pdf_btn = self.encontrar_botao_gerar_pdf(page)
                                
                            if not pdf_btn:
                                raise Exception("Botão 'Gerar PDF' não localizado na árvore.")
                                
                            # 5. Gera PDF
                            pdf_btn.click()
                            self.configurar_e_gerar_pdf(page, context, num_proc, export_dir)
                            
                            self.atualizar_status_processo(db_file, num_proc, "SUCESSO", prazo=prazo)
                            logger(f"  [SUCESSO] Processo {num_proc} exportado.", "INFO")
                            sucessos += 1
                            sucesso_proc = True
                            
                        except Exception as err:
                            ultimo_erro = str(err)
                            logger(f"  Tentativa {tentativa} falhou: {ultimo_erro}", "WARNING")
                            if tentativa < limite_tentativas:
                                time.sleep(2)
                                try:
                                    page.goto(url_base)
                                    page.wait_for_load_state("load")
                                    time.sleep(2)
                                except Exception:
                                    pass
                            tentativa += 1
                            
                    if not sucesso_proc:
                        self.atualizar_status_processo(db_file, num_proc, "FALHA", mensagem_erro=ultimo_erro, incrementar_tentativa=True)
                        logger(f"  [FALHA] Processo {num_proc} não foi exportado. Erro: {ultimo_erro}", "ERROR")
                        falhas += 1
                        
                    # Intervalo de segurança entre processos
                    if idx < total:
                        time.sleep(delay)
                        
            finally:
                browser.close()
                
        logger(f"Corrida finalizada. Sucessos: {sucessos}, Falhas: {falhas}, Ignorados: {ignorados}.", "INFO")
        
        return {
            "status": "sucesso",
            "sucessos": sucessos,
            "falhas": falhas,
            "ignorados": ignorados
        }
