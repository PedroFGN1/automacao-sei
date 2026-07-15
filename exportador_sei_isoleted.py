import os
import time
import sys
import sqlite3
from datetime import datetime
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

# === CONFIGURAÇÕES GERAIS ===
# COLOQUE A URL DO SEI DO SEU ÓRGÃO AQUI (ou crie um arquivo url_sei.txt contendo a URL)
SEI_URL = "https://[URL_DO_SEI_DO_SEU_ORGAO]"

USER_DATA_DIR = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes\perfil_sei"
EXPORT_DIR = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes"
PROCESS_FILE = "processos.txt"
DB_FILE = r"C:\Users\pedro.galvao\Documents\automacao.db"
DELAY_BETWEEN_PROCESSES = 4  # segundos (conforme requisito 8)

# Lista padrão de processos caso o arquivo processos.txt não exista ou esteja vazio
DEFAULT_PROCESS_LIST = [
    "202600004061428",
    "202600004061543",
    "202600004061769"
]

# ==============================================================================
# HELDERS DO BANCO DE DADOS (SQLITE)
# ==============================================================================
def inicializar_banco(processos):
    """Cria a tabela de controle e sincroniza com a lista de processos fornecida."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processos (
            numero_processo TEXT PRIMARY KEY,
            status TEXT NOT NULL,          -- PENDENTE, SUCESSO, FALHA
            tentativas INTEGER DEFAULT 0,
            ultima_execucao TEXT,
            mensagem_erro TEXT,
            prazo TEXT
        )
    """)
    conn.commit()
    
    # Migração automática se a tabela processos já existia sem a coluna 'prazo'
    try:
        cursor.execute("ALTER TABLE processos ADD COLUMN prazo TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    # Adicionar novos processos vindos do arquivo txt (deduplicando para evitar UNIQUE constraint failed)
    cursor.execute("SELECT numero_processo FROM processos")
    processos_no_db = {row[0] for row in cursor.fetchall()}
    
    processos_unicos = list(dict.fromkeys(processos))
    novos = [(p, "PENDENTE") for p in processos_unicos if p not in processos_no_db]
    if novos:
        cursor.executemany("INSERT OR IGNORE INTO processos (numero_processo, status) VALUES (?, ?)", novos)
        conn.commit()
        print(f"[*] Sincronizados {len(novos)} novos processos no banco de dados.")
        
    conn.close()

def obter_processos_a_executar(processos_txt):
    """Filtra a lista do processos.txt retornando apenas os que não são SUCESSO no banco."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT numero_processo FROM processos WHERE status = 'SUCESSO'")
    sucessos = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Retorna apenas os processos da lista do TXT que não são sucesso
    fila = [p for p in processos_txt if p not in sucessos]
    return fila

def atualizar_status_processo(numero_processo, status, mensagem_erro=None, incrementar_tentativa=False, prazo=None):
    """Atualiza o status, data de execução, mensagem de erro e prazo do processo."""
    conn = sqlite3.connect(DB_FILE)
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

# ==============================================================================
# HELPERS DE INTERFACE TEXTUAL & ARQUIVOS
# ==============================================================================
def carregar_processos():
    """Carrega e deduplica os números dos processos do arquivo processos.txt ou usa a lista padrão."""
    if not os.path.exists(PROCESS_FILE):
        print(f"[*] Criando arquivo '{PROCESS_FILE}' com processos de exemplo...")
        with open(PROCESS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_PROCESS_LIST) + "\n")
        return list(dict.fromkeys(DEFAULT_PROCESS_LIST))
    
    processos = []
    with open(PROCESS_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            proc = linha.strip()
            if proc and not proc.startswith("#"):
                processos.append(proc)
                
    if not processos:
        print(f"[!] Arquivo '{PROCESS_FILE}' está vazio. Usando a lista padrão...")
        return list(dict.fromkeys(DEFAULT_PROCESS_LIST))
        
    return list(dict.fromkeys(processos))

def verificar_pdf_valido(numero_processo):
    """Verifica se o arquivo PDF existe localmente e se tem tamanho válido (> 1 KB)."""
    pdf_path = os.path.join(EXPORT_DIR, f"{numero_processo}.pdf")
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        if size > 1024:  # Maior que 1 KB
            return True
    return False

def exibir_barra_progresso(index, total, sucessos, falhas, ignorados, tempo_inicio):
    """Gera uma barra de progresso em tempo real no terminal com estatísticas e ETA."""
    if total == 0:
        return
        
    percentual = (index / total) * 100
    largura_barra = 30
    preenchido = int(largura_barra * index // total)
    barra = "=" * preenchido + ">" + " " * (largura_barra - preenchido - 1)
    if index == total:
        barra = "=" * largura_barra
        
    # Calcular tempos
    tempo_decorrido = time.time() - tempo_inicio
    processados_efetivos = index - ignorados
    
    if processados_efetivos > 0:
        tempo_medio = tempo_decorrido / processados_efetivos
        restantes = total - index
        eta_segundos = restantes * tempo_medio
        
        eta_m, eta_s = divmod(int(eta_segundos), 60)
        eta_h, eta_m = divmod(eta_m, 60)
        eta_str = f"{eta_h:02d}h:{eta_m:02d}m:{eta_s:02d}s" if eta_h > 0 else f"{eta_m:02d}m:{eta_s:02d}s"
    else:
        eta_str = "--:--"
        
    dec_m, dec_s = divmod(int(tempo_decorrido), 60)
    dec_h, dec_m = divmod(dec_m, 60)
    dec_str = f"{dec_h:02d}h:{dec_m:02d}m:{dec_s:02d}s" if dec_h > 0 else f"{dec_m:02d}m:{dec_s:02d}s"
    
    sys.stdout.write("\r")
    sys.stdout.write(
        f"[{barra}] {percentual:5.1f}% | "
        f"Progresso: {index}/{total} | "
        f"Sucesso: {sucessos} | "
        f"Falha: {falhas} | "
        f"Ignorados: {ignorados} | "
        f"Tempo: {dec_str} | "
        f"ETA: {eta_str}"
    )
    sys.stdout.flush()

def gerar_relatorio_final(processos_lote, tempo_inicio, sucessos, falhas, ignorados):
    """Gera um relatório de execução textual consolidado na pasta de exportações."""
    agora_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    relatorio_path = os.path.join(EXPORT_DIR, f"relatorio_execucao_{agora_str}.txt")
    
    tempo_total = time.time() - tempo_inicio
    tot_m, tot_s = divmod(int(tempo_total), 60)
    tot_h, tot_m = divmod(tot_m, 60)
    tempo_total_str = f"{tot_h:02d}h:{tot_m:02d}m:{tot_s:02d}s" if tot_h > 0 else f"{tot_m:02d}m:{tot_s:02d}s"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT numero_processo, mensagem_erro FROM processos WHERE status = 'FALHA'")
    lista_falhas = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='SUCESSO' THEN 1 ELSE 0 END), SUM(CASE WHEN status='FALHA' THEN 1 ELSE 0 END), SUM(CASE WHEN status='PENDENTE' THEN 1 ELSE 0 END) FROM processos")
    total_db, sucesso_db, falha_db, pendente_db = cursor.fetchone()
    conn.close()
    
    with open(relatorio_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("             RELATÓRIO DE EXECUÇÃO - EXPORTADOR DE PROCESSOS SEI\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Data de Execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Duração Total da Corrida: {tempo_total_str}\n\n")
        
        f.write("ESTATÍSTICAS DO LOTE ATUAL:\n")
        f.write(f"- Total de processos na fila enviada: {len(processos_lote)}\n")
        f.write(f"- Sucessos obtidos nesta corrida: {sucessos}\n")
        f.write(f"- Falhas ocorridas nesta corrida: {falhas}\n")
        f.write(f"- Ignorados (já baixados anteriormente): {ignorados}\n\n")
        
        f.write("ESTATÍSTICAS GERAIS DO BANCO DE DADOS (ACUMULADO):\n")
        f.write(f"- Total Cadastrado: {total_db or 0}\n")
        f.write(f"- Total Sucesso: {sucesso_db or 0}\n")
        f.write(f"- Total Falha: {falha_db or 0}\n")
        f.write(f"- Total Restante (Pendente): {pendente_db or 0}\n\n")
        
        f.write("DETALHAMENTO DE PROCESSOS COM FALHA NO BANCO (AUDITORIA):\n")
        f.write("-" * 80 + "\n")
        if lista_falhas:
            for proc, msg in lista_falhas:
                f.write(f"Processo: {proc}\n")
                f.write(f"  Erro: {msg or 'Erro não especificado.'}\n")
                f.write("-" * 80 + "\n")
        else:
            f.write("Nenhum processo com falha registrado no banco de dados.\n")
            f.write("-" * 80 + "\n")
            
    print(f"\n\n[*] Relatório de execução gerado com sucesso em: {relatorio_path}")

# ==============================================================================
# LÓGICA DE INTERAÇÃO WEB (PLAYWRIGHT)
# ==============================================================================
def aguardar_login(page):
    """Aguarda até que o usuário esteja logado no SEI (busca rápida ou menu principal visíveis)."""
    print("[*] Aguardando login no SEI. Por favor, acesse o sistema no navegador aberto...")
    
    logado_selectors = [
        "#txtPesquisaRapida",
        "input[name='txtPesquisaRapida']",
        "a[href*='acao=procedimento_controlar']",
        "a:has-text('Controle de Processos')",
        "span:has-text('Controle de Processos')"
    ]
    
    tentativas = 0
    while True:
        # Verifica a página principal
        for sel in logado_selectors:
            try:
                if page.locator(sel).first.is_visible():
                    print("[+] Login detectado com sucesso!")
                    return True
            except Exception:
                pass
                
        # Verifica nos frames existentes
        for frame in page.frames:
            for sel in logado_selectors:
                try:
                    if frame.locator(sel).first.is_visible():
                        print("[+] Login detectado com sucesso (dentro de frame)!")
                        return True
                except Exception:
                    pass
                    
        tentativas += 1
        if tentativas % 10 == 0:
            print("[*] Ainda aguardando login no SEI... Por favor, conclua a autenticação na janela do navegador.")
            
        time.sleep(2)

def preencher_busca_rapida(page, numero_processo):
    """Localiza e preenche o campo de pesquisa rápida, enviando a busca."""
    selectors = [
        "#txtPesquisaRapida",
        "input[name='txtPesquisaRapida']",
        "input[placeholder*='Pesquisa']",
        "input[placeholder*='processo']"
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

def encontrar_botao_gerar_pdf(page):
    """Busca o botão de gerar PDF do processo seguindo a hierarquia de iframes do SEI 5.0.4."""
    selectors = [
        "a[href*='acao=procedimento_gerar_pdf']",
        "a[onclick*='acao=procedimento_gerar_pdf']",
        "a:has(img[src*='processo_gerar_pdf'])",
        "img[src*='processo_gerar_pdf']",
        "a[title*='Gerar Arquivo PDF']",
        "a[title*='Gerar PDF']",
        "a[title*='PDF']",
        "[title*='Gerar Arquivo PDF']"
    ]
    
    # 1. Tentar no frame '#ifrConteudoVisualizacao'
    try:
        frame_conteudo = page.frame_locator("#ifrConteudoVisualizacao")
        for sel in selectors:
            try:
                loc = frame_conteudo.locator(sel)
                if loc.first.is_visible():
                    return loc.first
            except Exception:
                pass
    except Exception:
        pass
            
    # 2. Fallback no frame '#ifrVisualizacao'
    try:
        frame_visualizacao = page.frame_locator("#ifrVisualizacao")
        for sel in selectors:
            try:
                loc = frame_visualizacao.locator(sel)
                if loc.first.is_visible():
                    return loc.first
            except Exception:
                pass
    except Exception:
        pass
        
    # 3. Fallback na raiz da página
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.first.is_visible():
                return loc.first
        except Exception:
            pass
            
    return None

def clicar_no_raiz_arvore(page, numero_processo):
    """Clica no nó principal (raiz) do processo na árvore para garantir a exibição da capa."""
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
            "a[id^='anchor']",
            "span[id^='span']"
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

def extrair_prazo_processo(page):
    """
    Tenta localizar o ícone de controle de prazo na árvore do processo (iframe ifrArvore)
    e extrai o conteúdo do atributo 'title' da imagem do prazo.
    Retorna o texto em linha única ou None se não encontrar ou se estiver sem prazo.
    """
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
                    prazo_limpo = " ".join(title.split())
                    return prazo_limpo
        except Exception:
            pass
            
    return None

def configurar_e_gerar_pdf(page, context, numero_processo):
    """Foca no iframe do visualizador de PDF, preenche as opções e executa o download."""
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
        "input[value='Gerar']",
        "button:has-text('Gerar')"
    ]
    
    submit_button = None
    for sel in submit_selectors:
        try:
            loc = frame.locator(sel)
            loc.first.wait_for(state="visible", timeout=15000)
            submit_button = loc.first
            break
        except Exception:
            pass
            
    if not submit_button:
        raise Exception("Botão 'Gerar' não encontrado no iframe de visualização.")

    # Selecionar o radio button "Todos os documentos disponíveis" (value='T')
    radio_selectors = [
        "input[value='T']",
        "input[name='rdoTipo'][value='T']",
        "input[name='rdoDocumento'][value='T']",
        "#rdoDocumentoTodos",
        "#rdoTipoT"
    ]
    
    radio_selected = False
    for sel in radio_selectors:
        try:
            loc = frame.locator(sel)
            if loc.first.is_visible():
                if not loc.first.is_checked():
                    loc.first.check()
                radio_selected = True
                break
        except Exception:
            pass
            
    if not radio_selected:
        labels = [
            "label:has-text('Todos')",
            "label:has-text('Todos os documentos disponíveis')",
            "text='Todos os documentos disponíveis'",
            "text='Todos'"
        ]
        for sel in labels:
            try:
                loc = frame.locator(sel)
                if loc.first.is_visible():
                    loc.first.click()
                    radio_selected = True
                    break
            except Exception:
                pass

    with page.expect_download(timeout=90000) as download_info:
        submit_button.click()
        
    download = download_info.value
    download_path = os.path.join(EXPORT_DIR, f"{numero_processo}.pdf")
    download.save_as(download_path)

# ==============================================================================
# FLUXO EXECUTOR PRINCIPAL
# ==============================================================================
def processar_exportacao():
    processos_txt = carregar_processos()
    
    # Inicializa banco SQLite
    inicializar_banco(processos_txt)
    
    # Filtra processos pendentes
    fila_execucao = obter_processos_a_executar(processos_txt)
    total_lote = len(fila_execucao)
    
    print(f"[*] Total de processos carregados do arquivo TXT: {len(processos_txt)}")
    print(f"[*] Processos a executar nesta rodada (pendentes/falhas): {total_lote}")
    
    if total_lote == 0:
        print("[+] Todos os processos da lista já foram exportados com sucesso! Encerrando...")
        return
        
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    # Resolução da URL do SEI
    url_atual = SEI_URL
    if "[URL_DO_SEI_DO_SEU_ORGAO]" in url_atual:
        if os.path.exists("url_sei.txt"):
            with open("url_sei.txt", "r", encoding="utf-8") as url_f:
                url_atual = url_f.read().strip()
        
        if "[URL_DO_SEI_DO_SEU_ORGAO]" in url_atual or not url_atual:
            print("[!] URL do SEI não configurada.")
            print("[!] Digite a URL de acesso ao SEI do seu órgão (ex: https://sei.orgao.gov.br):")
            try:
                url_atual = input("> ").strip()
                if url_atual:
                    with open("url_sei.txt", "w", encoding="utf-8") as url_f:
                        url_f.write(url_atual)
            except Exception:
                raise Exception("URL do SEI não configurada. Defina SEI_URL no script ou preencha url_sei.txt.")
                
    print("[*] Iniciando navegador Chrome isolado...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                channel="chrome",
                accept_downloads=True
            )
            
            try:
                page = context.pages[0]
                print(f"[*] Navegando para: {url_atual}")
                page.goto(url_atual)
                
                # Aguarda autenticação
                aguardar_login(page)
                
                page.set_default_timeout(15000)
                
                sucessos_corrida = 0
                falhas_corrida = 0
                ignorados_corrida = 0
                tempo_inicio = time.time()
                
                print("\n" + "=" * 80)
                print("                     INICIANDO EXPORTAÇÃO EM LOTE")
                print("=" * 80 + "\n")
                
                for index, numero_processo in enumerate(fila_execucao, 1):
                    # Atualiza o dashboard do terminal
                    exibir_barra_progresso(index - 1, total_lote, sucessos_corrida, falhas_corrida, ignorados_corrida, tempo_inicio)
                    
                    # 1. Auto-skip: Verifica se já existe um arquivo PDF válido
                    if verificar_pdf_valido(numero_processo):
                        atualizar_status_processo(numero_processo, "SUCESSO")
                        ignorados_corrida += 1
                        exibir_barra_progresso(index, total_lote, sucessos_corrida, falhas_corrida, ignorados_corrida, tempo_inicio)
                        continue
                        
                    # 2. Processar processo (com política de re-tentativa imediata)
                    tentativa = 1
                    limite_tentativas = 2
                    processo_sucesso = False
                    ultimo_erro = ""
                    prazo_detectado = None
                    
                    while tentativa <= limite_tentativas and not processo_sucesso:
                        try:
                            # Preenche barra de busca rápida
                            success_busca = preencher_busca_rapida(page, numero_processo)
                            if not success_busca:
                                page.reload()
                                page.wait_for_load_state("load")
                                time.sleep(2)
                                success_busca = preencher_busca_rapida(page, numero_processo)
                                if not success_busca:
                                    raise Exception("Pesquisa rápida não localizada.")

                            # Aguarda carregar contêiner principal da visualização
                            try:
                                page.wait_for_selector("#ifrConteudoVisualizacao", timeout=15000)
                            except Exception:
                                # Verifica alertas nativos do SEI
                                alert_selectors = [".infraMensagem", ".mensagem", "#mensagem", "text='não encontrado'", "text='inexistente'"]
                                alert_text = ""
                                for sel in alert_selectors:
                                    try:
                                        loc = page.locator(sel)
                                        if loc.is_visible():
                                            alert_text = loc.inner_text().strip()
                                            break
                                    except Exception:
                                        pass
                                if alert_text:
                                    raise Exception(f"Erro no SEI: '{alert_text}'")
                                else:
                                    raise Exception("Timeout aguardando carregamento do processo.")
                            
                            time.sleep(2.5)  # Renderização
                            
                            # Extrai o prazo se houver na árvore do processo
                            try:
                                prazo_detectado = extrair_prazo_processo(page)
                                if prazo_detectado:
                                    print(f"\n[*] Prazo identificado: {prazo_detectado}")
                            except Exception as pe:
                                print(f"\n[!] Erro ao tentar extrair prazo: {pe}")
                            
                            # Localiza o botão PDF
                            pdf_button = encontrar_botao_gerar_pdf(page)
                            if not pdf_button:
                                clicar_no_raiz_arvore(page, numero_processo)
                                time.sleep(2)
                                pdf_button = encontrar_botao_gerar_pdf(page)
                                
                            if not pdf_button:
                                raise Exception("Botão 'Gerar PDF' não encontrado.")
                                
                            # Clica e abre tela de configurações de PDF
                            pdf_button.click()
                            
                            # Executa configuração e download
                            configurar_e_gerar_pdf(page, context, numero_processo)
                            
                            # Sucesso!
                            atualizar_status_processo(numero_processo, "SUCESSO", incrementar_tentativa=True, prazo=prazo_detectado)
                            sucessos_corrida += 1
                            processo_sucesso = True
                            
                        except Exception as e:
                            ultimo_erro = str(e)
                            # Se falhou na 1ª tentativa, realiza re-tentativa imediata
                            if tentativa < limite_tentativas:
                                time.sleep(2)
                                # Reseta página para a URL base antes de re-tentar
                                try:
                                    page.goto(url_atual)
                                    aguardar_login(page)
                                except Exception:
                                    pass
                            tentativa += 1
                            
                    if not processo_sucesso:
                        atualizar_status_processo(numero_processo, "FALHA", mensagem_erro=ultimo_erro, incrementar_tentativa=True)
                        falhas_corrida += 1
                        
                    # Atualiza progress bar ao finalizar
                    exibir_barra_progresso(index, total_lote, sucessos_corrida, falhas_corrida, ignorados_corrida, tempo_inicio)
                    
                    # Intervalo de segurança
                    if index < total_lote:
                        time.sleep(DELAY_BETWEEN_PROCESSES)
                        
                # Gerar relatório final de execução
                gerar_relatorio_final(fila_execucao, tempo_inicio, sucessos_corrida, falhas_corrida, ignorados_corrida)
                
            finally:
                context.close()
                
    except Exception as launch_err:
        print(f"\n[FATAL] Ocorreu uma exceção crítica no executor: {launch_err}")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        
    print("=" * 80)
    print("      PIPELINE DE EXPORTAÇÃO SEI - NAVEGADOR ISOLADO PERSISTENTE")
    print("=" * 80)
    processar_exportacao()
