import os
import time
import sys
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

# === CONFIGURAÇÕES GERAIS ===
# COLOQUE A URL DO SEI DO SEU ÓRGÃO AQUI (ou crie um arquivo url_sei.txt contendo a URL)
SEI_URL = "https://[URL_DO_SEI_DO_SEU_ORGAO]"

USER_DATA_DIR = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes\perfil_sei"
EXPORT_DIR = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes"
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

def dump_debug_info(page, numero_processo):
    """Gera logs de depuração avançados salvando prints, árvore DOM e HTML dos iframes."""
    print("\n" + "!" * 80)
    print(f"[DEBUG DUMP] INICIANDO DIAGNÓSTICO DE ELEMENTOS PARA O PROCESSO: {numero_processo}")
    print("!" * 80)
    
    debug_dir = r"C:\SEI_Exportacoes\debug_info"
    os.makedirs(debug_dir, exist_ok=True)
    
    # 1. Capturar e salvar screenshot da página inteira
    screenshot_path = os.path.join(debug_dir, f"screenshot_{numero_processo}.png")
    try:
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"[DEBUG] Screenshot salvo em: {screenshot_path}")
    except Exception as e:
        print(f"[DEBUG] [ERRO] Falha ao tirar screenshot: {e}")
        
    # 2. Dump da hierarquia de frames
    hierarchy_path = os.path.join(debug_dir, f"hierarquia_frames_{numero_processo}.txt")
    try:
        with open(hierarchy_path, "w", encoding="utf-8") as f:
            f.write(f"PROCESSO: {numero_processo}\n")
            f.write(f"URL PRINCIPAL: {page.url}\n")
            f.write(f"TÍTULO DA PÁGINA: {page.title()}\n\n")
            f.write("HIERARQUIA COMPLETA DE IFRAMES NO DOM:\n")
            
            def dump_frame(fr, indent=""):
                f.write(f"{indent}- Frame Name: '{fr.name}', ID/Atributos: '{fr.url}'\n")
                for child in fr.child_frames:
                    dump_frame(child, indent + "  ")
                    
            for top_fr in page.main_frame.child_frames:
                dump_frame(top_fr, "  ")
        print(f"[DEBUG] Hierarquia de frames salva em: {hierarchy_path}")
    except Exception as e:
        print(f"[DEBUG] [ERRO] Falha ao mapear hierarquia de frames: {e}")
        
    # 3. Dump HTML de cada frame carregado
    try:
        # Conteúdo do documento principal
        main_html_path = os.path.join(debug_dir, f"html_pagina_principal_{numero_processo}.html")
        with open(main_html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
            
        # Conteúdo individual de cada frame
        for i, fr in enumerate(page.frames):
            fr_name = fr.name if fr.name else f"frame_sem_nome_{i}"
            # Limpa caracteres especiais do nome para salvar o arquivo
            safe_name = "".join(c for c in fr_name if c.isalnum() or c in ("-", "_"))
            fr_html_path = os.path.join(debug_dir, f"html_frame_{safe_name}_{numero_processo}.html")
            with open(fr_html_path, "w", encoding="utf-8") as f:
                f.write(fr.content())
        print(f"[DEBUG] Dumps HTML salvos na pasta: {debug_dir}")
    except Exception as e:
        print(f"[DEBUG] [ERRO] Falha ao realizar dump de código HTML: {e}")
        
    # 4. Análise e varredura heurística de elementos
    analysis_path = os.path.join(debug_dir, f"analise_elementos_{numero_processo}.txt")
    try:
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(f"ANÁLISE HEURÍSTICA DE LINKS E BOTÕES - PROCESSO: {numero_processo}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, fr in enumerate(page.frames):
                fr_name = fr.name if fr.name else f"sem_nome_{i}"
                f.write(f"--- FRAME: '{fr_name}' (URL: {fr.url}) ---\n")
                
                # Links <a>
                try:
                    links = fr.locator("a").all()
                    f.write(f"Links (<a>) localizados: {len(links)}\n")
                    for idx, link in enumerate(links):
                        try:
                            href = link.get_attribute("href") or ""
                            onclick = link.get_attribute("onclick") or ""
                            title = link.get_attribute("title") or ""
                            text = link.inner_text().strip()
                            inner_html = link.inner_html().strip()
                            
                            # Filtro heurístico para termos de interesse em automações do SEI
                            if any(word in (href + onclick + title + text + inner_html).lower() for word in ["pdf", "gerar", "procedimento", "print", "documento"]):
                                f.write(f"  [LINK {idx}]:\n")
                                f.write(f"    Texto Visível: '{text}'\n")
                                f.write(f"    href: '{href}'\n")
                                f.write(f"    onclick: '{onclick}'\n")
                                f.write(f"    title: '{title}'\n")
                                f.write(f"    Inner HTML: {inner_html[:150]}...\n\n")
                        except Exception:
                            pass
                except Exception as e:
                    f.write(f"  [ERRO ao ler links]: {e}\n")
                    
                # Imagens <img>
                try:
                    imgs = fr.locator("img").all()
                    f.write(f"Imagens (<img>) localizadas: {len(imgs)}\n")
                    for idx, img in enumerate(imgs):
                        try:
                            src = img.get_attribute("src") or ""
                            title = img.get_attribute("title") or ""
                            alt = img.get_attribute("alt") or ""
                            
                            if any(word in (src + title + alt).lower() for word in ["pdf", "gerar", "print", "processo"]):
                                f.write(f"  [IMG {idx}]:\n")
                                f.write(f"    src: '{src}'\n")
                                f.write(f"    title: '{title}'\n")
                                f.write(f"    alt: '{alt}'\n\n")
                        except Exception:
                            pass
                except Exception as e:
                    f.write(f"  [ERRO ao ler imagens]: {e}\n")
                
                f.write("\n" + "-"*80 + "\n\n")
        print(f"[DEBUG] Análise heurística salva em: {analysis_path}")
    except Exception as e:
        print(f"[DEBUG] [ERRO] Falha ao executar varredura de elementos: {e}")
        
    print("!" * 80)
    print(f"[DEBUG DUMP] DIAGNÓSTICO CONCLUÍDO PARA: {numero_processo}")
    print("!" * 80 + "\n")

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
    """Busca o botão de gerar PDF do processo seguindo a hierarquia de iframes aninhados do SEI 5.0.4."""
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
    
    # 1. Fluxo Principal: Encadeamento de frames (#ifrVisualizacao -> #ifrConteudoVisualizacao)
    # No SEI 5.0.4, o botão do PDF reside fisicamente dentro do frame filho #ifrConteudoVisualizacao.
    try:
        frame_filho = page.frame_locator("#ifrVisualizacao").frame_locator("#ifrConteudoVisualizacao")
        for sel in selectors:
            try:
                loc = frame_filho.locator(sel)
                if loc.first.is_visible():
                    print(f"[*] Botão 'Gerar PDF' localizado via frames aninhados (seletor: '{sel}')")
                    return loc.first
            except Exception:
                pass
    except Exception as e:
        print(f"[!] Erro ao tentar buscar botão nos frames aninhados: {e}")
            
    # 2. Bloco de Fallback: Se o fluxo aninhado falhar, tenta nos contextos separados
    # Tentativa no contexto global (página raiz)
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.first.is_visible():
                print(f"[*] [Fallback] Botão 'Gerar PDF' localizado na raiz (seletor: '{sel}')")
                return loc.first
        except Exception:
            pass
            
    # Tentativa nos frames individuais
    frame_names = ["ifrConteudoVisualizacao", "ifrVisualizacao", "ifrArvore"]
    for frame_name in frame_names:
        for f in page.frames:
            if f.name == frame_name or frame_name in f.url:
                for sel in selectors:
                    try:
                        loc = f.locator(sel)
                        if loc.first.is_visible():
                            print(f"[*] [Fallback] Botão 'Gerar PDF' localizado no frame '{frame_name}' (seletor: '{sel}')")
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
                
    print("[*] Iniciando navegador Chrome isolado em modo depuração...")
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
                    # Monitora o iframe principal da visualização da direita (#ifrVisualizacao)
                    try:
                        page.wait_for_selector("#ifrVisualizacao", timeout=15000)
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
                            # Tenta realizar dump se não encontrar visualização
                            dump_debug_info(page, numero_processo)
                            raise Exception("Timeout aguardando o carregamento do iframe de visualização.")
                    
                    # Garante um tempo de renderização para o iframe interno filho (#ifrConteudoVisualizacao)
                    print("[*] Aguardando renderização do painel interno...")
                    time.sleep(2.5)
                    
                    # Passo 3 & 4: Buscar o botão Gerar PDF (Seguindo a hierarquia de frames aninhados)
                    pdf_button = encontrar_botao_gerar_pdf(page)
                    
                    # Se não achou de primeira, força o clique no nó raiz na árvore
                    if not pdf_button:
                        clicar_no_raiz_arvore(page, numero_processo)
                        time.sleep(2)
                        pdf_button = encontrar_botao_gerar_pdf(page)
                        
                    if not pdf_button:
                        # Executa o dump de debug avançado!
                        dump_debug_info(page, numero_processo)
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
    print("      DIAGNÓSTICO EXPORTADOR SEI - DEBUG")
    print("=" * 60)
    processar_exportacao()
