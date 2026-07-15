import customtkinter as ctk
import threading
from ui.components.paginated_table import PaginatedTable
from ui.components.log_viewer import LogViewer
import core.database as db
from procedures import PROCEDURES, carregar_procedimentos_dinamicamente

class App(ctk.CTk):
    """
    Janela Principal do Gerenciador de Automações SEI Modular.
    """
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("Gerenciador Modular de Automações SEI")
        self.geometry("1100x680")
        
        # Tema Escuro e Estética Premium
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variáveis de Controle
        self.procedimento_ativo = None
        self.campos_dinamicos = {} # { "CAMPO_ID": CTkEntry | CTkEntry(password) | CTkEntry(path) }
        self.thread_execucao = None
        
        # Garante que os procedimentos estejam carregados do pacote
        carregar_procedimentos_dinamicamente()
        
        self.criar_layout()
        
    def criar_layout(self):
        # Grid layout (1 linha, 2 colunas principais)
        self.grid_columnconfigure(0, weight=3, minsize=380) # Painel de Controle (Esquerdo)
        self.grid_columnconfigure(1, weight=7, minsize=680) # Painel de Visualização (Direito)
        self.grid_rowconfigure(0, weight=1)
        
        self.criar_painel_esquerdo()
        self.criar_painel_direito()

    def criar_painel_esquerdo(self):
        # Painel de controle esquerdo com bordas suaves
        sidebar = ctk.CTkFrame(self, fg_color="#181818", corner_radius=12, border_color="#2c2c2c", border_width=1)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Título do Painel
        lbl_titulo = ctk.CTkLabel(
            sidebar, 
            text="AUTOMAÇÕES SEI", 
            font=ctk.CTkFont(family="Outfit", size=18, weight="bold"),
            text_color="#1f538d"
        )
        lbl_titulo.pack(fill="x", pady=(20, 10))
        
        # Seletor de Automação
        lbl_sel = ctk.CTkLabel(sidebar, text="Selecione o Procedimento:", font=ctk.CTkFont(size=12))
        lbl_sel.pack(fill="x", padx=20, anchor="w", pady=(10, 2))
        
        opcoes = list(PROCEDURES.keys())
        self.select_menu = ctk.CTkOptionMenu(
            sidebar,
            values=opcoes if opcoes else ["Nenhum Encontrado"],
            fg_color="#1f538d",
            button_color="#153b65",
            button_hover_color="#2a6fb8",
            corner_radius=6,
            command=self.mudar_procedimento
        )
        self.select_menu.pack(fill="x", padx=20, pady=(0, 15))
        
        # Área de Rolagem do Formulário Dinâmico
        self.form_scroll = ctk.CTkScrollableFrame(
            sidebar, 
            fg_color="#121212", 
            corner_radius=8,
            scrollbar_button_color="#303030"
        )
        self.form_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botão Iniciar Automação (Premium)
        self.btn_iniciar = ctk.CTkButton(
            sidebar,
            text="Iniciar Automação",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f538d",
            hover_color="#2a6fb8",
            height=45,
            corner_radius=8,
            command=self.iniciar_automacao
        )
        self.btn_iniciar.pack(fill="x", padx=20, pady=20)
        
        # Inicializa o formulário padrão com o primeiro procedimento
        if opcoes:
            self.mudar_procedimento(opcoes[0])

    def criar_painel_direito(self):
        # Painel direito contendo o tabview principal
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color="#181818", 
            segmented_button_fg_color="#121212",
            segmented_button_selected_color="#1f538d",
            segmented_button_selected_hover_color="#2a6fb8"
        )
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Abas
        tab_dados = self.tabview.add("Processos Locais")
        tab_logs = self.tabview.add("Console de Execução")
        
        # Tabela paginada (Aba 1)
        self.tabela = PaginatedTable(
            tab_dados,
            carregar_dados_callback=db.obter_processos_paginados,
            obter_total_callback=db.obter_total_processos,
            itens_por_pagina=8
        )
        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Console de logs (Aba 2)
        self.log_viewer = LogViewer(tab_logs)
        self.log_viewer.pack(fill="both", expand=True, padx=10, pady=10)

    def mudar_procedimento(self, nome_classe):
        if nome_classe not in PROCEDURES:
            return
            
        # Limpa formulário antigo
        for child in self.form_scroll.winfo_children():
            child.destroy()
        self.campos_dinamicos.clear()
        
        # Instancia temporariamente para ler as configs
        self.procedimento_ativo = PROCEDURES[nome_classe]()
        
        # Renderiza configurações dinâmicas
        self.renderizar_campos(self.procedimento_ativo.fixed_settings, "Configurações Fixas")
        self.renderizar_campos(self.procedimento_ativo.variable_settings, "Configurações de Execução")

    def renderizar_campos(self, settings_dict, titulo_secao):
        if not settings_dict:
            return
            
        # Divisor visual da seção
        lbl_sec = ctk.CTkLabel(
            self.form_scroll, 
            text=titulo_secao.upper(), 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888888",
            anchor="w"
        )
        lbl_sec.pack(fill="x", pady=(15, 5))
        
        for campo_id, config in settings_dict.items():
            # Rótulo do campo
            lbl_campo = ctk.CTkLabel(self.form_scroll, text=config.get("label", campo_id), font=ctk.CTkFont(size=12), anchor="w")
            lbl_campo.pack(fill="x", pady=(5, 1))
            
            # Tipo de campo
            tipo = config.get("type", "string")
            default_val = config.get("default", "")
            
            if tipo == "password":
                entry = ctk.CTkEntry(self.form_scroll, show="*", fg_color="#1c1c1c", border_color="#303030", corner_radius=6, height=30)
            else:
                entry = ctk.CTkEntry(self.form_scroll, fg_color="#1c1c1c", border_color="#303030", corner_radius=6, height=30)
                
            entry.insert(0, default_val)
            entry.pack(fill="x", pady=(0, 5))
            
            # Salva referência do campo
            self.campos_dinamicos[campo_id] = entry
            
            # Descrição rápida se houver
            desc = config.get("description", "")
            if desc:
                lbl_desc = ctk.CTkLabel(
                    self.form_scroll, 
                    text=desc, 
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color="#666666",
                    anchor="w",
                    wraplength=300,
                    justify="left"
                )
                lbl_desc.pack(fill="x", pady=(0, 10))

    def iniciar_automacao(self):
        if not self.procedimento_ativo:
            return
            
        # Coleta configurações
        config_valores = {}
        for campo_id, entry in self.campos_dinamicos.items():
            config_valores[campo_id] = entry.get().strip()
            
        # Altera estados visuais de execução
        self.btn_iniciar.configure(state="disabled", text="Executando Automação...")
        self.select_menu.configure(state="disabled")
        self.log_viewer.limpar_logs()
        self.tabview.select("Console de Execução")
        
        # Roda na thread secundária para não congelar o CustomTkinter
        self.thread_execucao = threading.Thread(
            target=self.executar_procedimento_worker, 
            args=(self.procedimento_ativo, config_valores)
        )
        self.thread_execucao.daemon = True
        self.thread_execucao.start()

    def executar_procedimento_worker(self, procedimento, settings):
        def thread_safe_log(msg):
            # Envia o log para a thread da UI de forma segura
            self.after(0, self.log_viewer.adicionar_log, msg)
            
        sucesso = False
        try:
            sucesso = procedimento.run(settings, log_callback=thread_safe_log)
        except Exception as exc:
            thread_safe_log(f"ERRO CRÍTICO NA EXECUÇÃO: {exc}")
            
        # Finaliza e atualiza elementos visuais na thread principal da UI
        self.after(0, self.finalizar_execucao_ui, sucesso)

    def finalizar_execucao_ui(self, sucesso):
        self.btn_iniciar.configure(state="normal", text="Iniciar Automação")
        self.select_menu.configure(state="normal")
        
        # Alerta final no log
        status_msg = "AUTOMAÇÃO CONCLUÍDA COM SUCESSO." if sucesso else "FALHA NA EXECUÇÃO DO PROCEDIMENTO."
        self.log_viewer.adicionar_log(f"\n>>> {status_msg} <<<")
        
        # Atualiza a tabela de processos para mostrar possíveis mudanças de status
        self.tabela.atualizar_tabela()
