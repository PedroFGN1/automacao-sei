import os
import time
import sys
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

# === CONFIGURAÇÕES GERAIS ===
# COLOQUE A URL DO SEI DO SEU ÓRGÃO AQUI (ou crie um arquivo url_sei.txt contendo a URL)
SEI_URL = "https://[URL_DO_SEI_DO_SEU_ORGAO]"

USER_DATA_DIR = r"C:\SEI_Exportacoes\perfil_sei"
EXPORT_DIR = r"C:\SEI_Exportacoes"
PROCESS_FILE = "processos.txt"
DELAY_BETWEEN_PROCESSES = 4  # segundos (conforme requisito 8)

# Lista padrão de processos caso o arquivo processos.txt não exista ou esteja vazio
DEFAULT_PROCESS_LIST = [
    "202600004061428",
    "202600004061543",
    "202600004061769"
]

def carregar_processos():
    """Carrega os números dos processos do arquivo processos.txt ou usa a lista padrão."""
    if not os.path.exists(PROCESS_FILE):
        print(f"[*] Criando arquivo '{PROCESS_FILE}' com processos de exemplo...")
        with open(PROCESS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_PROCESS_LIST) + "\n")
        return DEFAULT_PROCESS_LIST
    
    processos = []
    with open(PROCESS_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            proc = linha.strip()
            if proc and not proc.startswith("#"):
                processos.append(proc)
                
    if not processos:
        print(f"[!] Arquivo '{PROCESS_FILE}' está vazio. Usando a lista padrão...")
        return DEFAULT_PROCESS_LIST
        
    return processos

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
    
    # 1. Tentar na página principal (raiz)
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
            
    # 2. Tentar em todos os frames da página
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
    
    # No SEI 5.0.4, o botão do PDF reside fisicamente no painel da direita 'ifrConteudoVisualizacao'.
    # 1. Tentar diretamente no frame '#ifrConteudoVisualizacao'
    try:
        frame_conteudo = page.frame_locator("#ifrConteudoVisualizacao")
        for sel in selectors:
            try:
                loc = frame_conteudo.locator(sel)
                if loc.first.is_visible():
                    print(f"[*] Botão 'Gerar PDF' localizado no frame '#ifrConteudoVisualizacao' (seletor: '{sel}')")
                    return loc.first
            except Exception:
                pass
    except Exception as e:
        print(f"[!] Erro ao buscar botão no frame '#ifrConteudoVisualizacao': {e}")
            
    # 2. Fallbacks em caso de telas ou versões diferentes
    # Fallback no frame '#ifrVisualizacao'
    try:
        frame_visualizacao = page.frame_locator("#ifrVisualizacao")
        for sel in selectors:
            try:
                loc = frame_visualizacao.locator(sel)
                if loc.first.is_visible():
                    print(f"[*] [Fallback] Botão 'Gerar PDF' localizado no frame '#ifrVisualizacao' (seletor: '{sel}')")
                    return loc.first
            except Exception:
                pass
    except Exception:
        pass
        
    # Fallback no contexto global da página raiz
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.first.is_visible():
                print(f"[*] [Fallback] Botão 'Gerar PDF' localizado na raiz (seletor: '{sel}')")
                return loc.first
        except Exception:
            pass
            
    # Fallback geral iterando por todos os frames da página
    for f in page.frames:
        for sel in selectors:
            try:
                loc = f.locator(sel)
                if loc.first.is_visible():
                    print(f"[*] [Fallback] Botão localizado no frame genérico '{f.name}'")
                    return loc.first
            except Exception:
                pass
                
    return None

def clicar_no_raiz_arvore(page, numero_processo):
    """Clica no nó principal (raiz) do processo na árvore para garantir a exibição da capa."""
    print("[*] Botão PDF não encontrado de imediato. Forçando seleção da raiz do processo...")
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
                    print(f"[*] Nó raiz selecionado na árvore via: '{c}'")
                    return True
            except Exception:
                pass
    return False

def configurar_e_gerar_pdf(page, context, numero_processo):
    """Foca no iframe do visualizador de PDF, preenche as opções e executa o download."""
    # No SEI 5.0.4, as opções de PDF carregam dentro do frame filho '#ifrVisualizacao' (aninhado em '#ifrConteudoVisualizacao')
    # 1. Tentar obter o frame aninhado
    frame = None
    try:
        frame = page.frame_locator("#ifrConteudoVisualizacao").frame_locator("#ifrVisualizacao")
    except Exception:
        pass
        
    # Fallback para o frame direto '#ifrVisualizacao'
    if not frame:
        frame = page.frame_locator("#ifrVisualizacao")
        
    # 2. Localizar o botão de submissão 'btnGerar'
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
            print(f"[*] Botão 'Gerar' encontrado no iframe com o seletor: '{sel}'")
            break
        except Exception:
            pass
            
    if not submit_button:
        raise Exception("A tela de configuração de geração do PDF não foi exibida (botão 'Gerar' não encontrado no iframe de visualização).")

    # 3. Selecionar o radio button "Todos os documentos disponíveis"
    # O SEI 5.0.4 geralmente usa o valor 'T' (input[value='T'])
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
                print(f"[*] Radio button 'Todos os documentos' marcado via: '{sel}'")
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
                    print(f"[*] Opção marcada via texto/label: '{sel}'")
                    break
            except Exception:
                pass
                
    if not radio_selected:
        print("[!] Aviso: Não foi possível garantir a seleção do radio button de forma programática. Tentando prosseguir com a opção padrão...")

    # 4. Interceptar o download e clicar em Gerar
    print("[*] Clicando em 'Gerar' e aguardando interceptação do download...")
    
    with page.expect_download(timeout=90000) as download_info:  # tolerância de 90s para PDFs gigantes
        submit_button.click()
        
    download = download_info.value
    download_path = os.path.join(EXPORT_DIR, f"{numero_processo}.pdf")
    download.save_as(download_path)
    print(f"[+] Download concluído! Arquivo salvo em: {download_path}")

def processar_exportacao():
    processos = carregar_processos()
    print(f"[*] Total de processos carregados para exportar: {len(processos)}")
    
    # Garante a existência do diretório de destino
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    print(f"[*] Diretório de exportação configurado: {EXPORT_DIR}")
    print(f"[*] Pasta de dados do perfil do navegador: {USER_DATA_DIR}")
    
    # Resolução da URL
    url_atual = SEI_URL
    if "[URL_DO_SEI_DO_SEU_ORGAO]" in url_atual:
        # Tenta ler de url_sei.txt
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
                raise Exception("URL do SEI não foi informada. Configure a variável 'SEI_URL' no script ou crie o arquivo 'url_sei.txt'.")
                
    print("[*] Iniciando navegador Chrome isolado...")
    try:
        with sync_playwright() as p:
            # Abre navegador isolado e persistente
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                channel="chrome",
                accept_downloads=True
            )
            
            # Obtém a primeira página criada pelo navegador persistente
            page = context.pages[0]
            
            print(f"[*] Navegando para o SEI: {url_atual}")
            page.goto(url_atual)
            
            # Aguarda login se for a primeira execução ou se a sessão expirou
            aguardar_login(page)
            
            # Garante tempo padrão de espera para operações normais
            page.set_default_timeout(15000)
            
            for index, numero_processo in enumerate(processos, 1):
                print("-" * 60)
                print(f"[{index}/{len(processos)}] Iniciando processamento do processo: {numero_processo}")
                
                try:
                    # Passo 1: Inserir processo e dar enter na busca rápida
                    success_busca = preencher_busca_rapida(page, numero_processo)
                    if not success_busca:
                        print("[*] Pesquisa rápida não disponível nesta tela. Atualizando página principal...")
                        page.reload()
                        page.wait_for_load_state("load")
                        time.sleep(2)
                        success_busca = preencher_busca_rapida(page, numero_processo)
                        if not success_busca:
                            raise Exception("Não foi possível localizar o campo de busca rápida '#txtPesquisaRapida' na tela.")

                    # Passo 2: Aguardar o carregamento da página do processo
                    # Monitora o contêiner principal da direita (#ifrConteudoVisualizacao)
                    try:
                        page.wait_for_selector("#ifrConteudoVisualizacao", timeout=15000)
                    except Exception:
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
                            raise Exception("Timeout aguardando o carregamento do painel do processo.")
                    
                    # Garante um tempo de renderização para o iframe interno
                    print("[*] Aguardando renderização do painel interno...")
                    time.sleep(2.5)
                    
                    # Passo 3 & 4: Buscar o botão Gerar PDF
                    pdf_button = encontrar_botao_gerar_pdf(page)
                    
                    # Se não achou de primeira, força o clique no nó raiz na árvore
                    if not pdf_button:
                        clicar_no_raiz_arvore(page, numero_processo)
                        time.sleep(2)
                        pdf_button = encontrar_botao_gerar_pdf(page)
                        
                    if not pdf_button:
                        raise Exception("Botão 'Gerar PDF do Processo' (acao=procedimento_gerar_pdf) não foi localizado na interface.")
                        
                    # Passo 5: Clicar no botão (carregará as opções no iframe #ifrVisualizacao)
                    print("[*] Clicando no ícone 'Gerar PDF' do processo...")
                    pdf_button.click()
                    
                    # Passo 6 & 7: Ajustar configurações de PDF e baixar
                    configurar_e_gerar_pdf(page, context, numero_processo)
                    
                except Exception as proc_err:
                    print(f"[ERROR] Falha ao exportar processo {numero_processo}: {proc_err}")
                
                # Passo 8: Intervalo de segurança antes de prosseguir
                if index < len(processos):
                    print(f"[*] Aguardando intervalo de segurança de {DELAY_BETWEEN_PROCESSES} segundos...")
                    time.sleep(DELAY_BETWEEN_PROCESSES)
                    
            print("=" * 60)
            print("[+] Processamento de lote concluído!")
            context.close()
            
    except Exception as launch_err:
        print(f"[FATAL] Erro ao iniciar ou interagir com o navegador Chrome isolado: {launch_err}")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        
    print("=" * 60)
    print("      EXPORTADOR SEI ISOLADO (PERSISTENTE) - PDF")
    print("=" * 60)
    processar_exportacao()
