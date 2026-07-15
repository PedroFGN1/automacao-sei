import customtkinter as ctk

class PaginatedTable(ctk.CTkFrame):
    """
    Componente visual de tabela paginada com barra de busca integrada.
    """
    def __init__(self, master, carregar_dados_callback, obter_total_callback, itens_por_pagina=7, **kwargs):
        super().__init__(master, **kwargs)
        
        self.carregar_dados = carregar_dados_callback
        self.obter_total = obter_total_callback
        self.itens_por_pagina = itens_por_pagina
        self.pagina_atual = 1
        self.total_paginas = 1
        
        # Design System (Cores elegantes)
        self.primary_color = "#1f538d"
        self.hover_color = "#2a6fb8"
        self.bg_card = "#2b2b2b"
        self.text_muted = "#aaaaaa"
        
        self.configure(fg_color="transparent")
        
        # Criação do layout
        self.criar_barra_busca()
        self.criar_cabecalho_tabela()
        self.criar_area_conteudo()
        self.criar_barra_paginacao()
        
        # Carrega dados iniciais
        self.atualizar_tabela()

    def criar_barra_busca(self):
        # Frame de busca com visual premium
        search_frame = ctk.CTkFrame(self, fg_color="#202020", height=50, corner_radius=8)
        search_frame.pack(fill="x", pady=(0, 10))
        search_frame.pack_propagate(False)
        
        # Campo de entrada
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Buscar por número ou tipo de processo...",
            fg_color="#181818",
            border_color="#3c3c3c",
            height=34,
            corner_radius=6
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        self.search_entry.bind("<Return>", lambda e: self.buscar())
        
        # Botão de busca
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Pesquisar",
            fg_color=self.primary_color,
            hover_color=self.hover_color,
            width=90,
            height=34,
            corner_radius=6,
            command=self.buscar
        )
        btn_buscar.pack(side="right", padx=(0, 10), pady=8)
        
        # Botão de limpar
        btn_limpar = ctk.CTkButton(
            search_frame,
            text="Limpar",
            fg_color="#3a3a3a",
            hover_color="#4f4f4f",
            width=70,
            height=34,
            corner_radius=6,
            command=self.limpar_busca
        )
        btn_limpar.pack(side="right", padx=(0, 5), pady=8)

    def criar_cabecalho_tabela(self):
        header_frame = ctk.CTkFrame(self, fg_color="#181818", height=35, corner_radius=4)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Colunas
        headers = [("Número do Processo", 0.35), ("Tipo de Procedimento", 0.30), ("Status", 0.15), ("Última Atualização", 0.20)]
        for text, weight in headers:
            lbl = ctk.CTkLabel(
                header_frame, 
                text=text, 
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                text_color="#ffffff"
            )
            # Layout proporcional aproximado
            lbl.pack(side="left", fill="both", expand=True, padx=10)

    def criar_area_conteudo(self):
        # Área de rolagem para os registros
        self.content_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="#151515", 
            scrollbar_button_color="#3a3a3a",
            scrollbar_button_hover_color="#555555",
            corner_radius=8
        )
        self.content_frame.pack(fill="both", expand=True)

    def criar_barra_paginacao(self):
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.nav_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Anterior
        self.btn_prev = ctk.CTkButton(
            self.nav_frame,
            text="Anterior",
            width=80,
            height=30,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            corner_radius=6,
            command=self.pagina_anterior
        )
        self.btn_prev.pack(side="left")
        
        # Indicador de Página
        self.lbl_page = ctk.CTkLabel(
            self.nav_frame,
            text="Página 1 de 1",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_page.pack(side="left", expand=True)
        
        # Contador total
        self.lbl_total = ctk.CTkLabel(
            self.nav_frame,
            text="Total: 0 processos",
            font=ctk.CTkFont(size=11),
            text_color=self.text_muted
        )
        self.lbl_total.pack(side="right", padx=(0, 10))
        
        # Botão Próximo
        self.btn_next = ctk.CTkButton(
            self.nav_frame,
            text="Próximo",
            width=80,
            height=30,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            corner_radius=6,
            command=self.proxima_pagina
        )
        self.btn_next.pack(side="right")

    def buscar(self):
        self.pagina_atual = 1
        self.atualizar_tabela()

    def limpar_busca(self):
        self.search_entry.delete(0, "end")
        self.pagina_atual = 1
        self.atualizar_tabela()

    def pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_tabela()

    def proxima_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_tabela()

    def atualizar_tabela(self):
        # Limpa conteúdo existente
        for child in self.content_frame.winfo_children():
            child.destroy()
            
        busca = self.search_entry.get().strip()
        
        # Busca total para paginação
        total_registros = self.obter_total(busca)
        self.total_paginas = max(1, (total_registros + self.itens_por_pagina - 1) // self.itens_por_pagina)
        
        # Ajusta página atual se ultrapassar
        if self.pagina_atual > self.total_paginas:
            self.pagina_atual = self.total_paginas
            
        # Carrega dados paginados
        dados = self.carregar_dados(self.pagina_atual, self.itens_por_pagina, busca)
        
        # Renderiza linhas
        for i, proc in enumerate(dados):
            row_bg = "#1e1e1e" if i % 2 == 0 else "#252525"
            row_frame = ctk.CTkFrame(self.content_frame, fg_color=row_bg, height=40, corner_radius=4)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)
            
            # Cores de Status dinâmicas
            status_text = proc.get("status", "PENDENTE")
            status_color = "#e5c158" # Amarelo (PENDENTE/PROCESSANDO)
            if status_text == "PROCESSADO":
                status_color = "#4ebb5a" # Verde
            elif status_text == "ERRO":
                status_color = "#dd514c" # Vermelho
                
            # Formata data para exibição simplificada
            data_raw = proc.get("data_atualizacao", "")
            data_format = data_raw.split(".")[0].replace("T", " ") if "T" in data_raw else data_raw
            
            # Label Numero
            lbl_num = ctk.CTkLabel(row_frame, text=proc.get("numero", ""), font=ctk.CTkFont(size=12), anchor="w")
            lbl_num.pack(side="left", fill="both", expand=True, padx=10)
            
            # Label Tipo
            lbl_tipo = ctk.CTkLabel(row_frame, text=proc.get("tipo", ""), font=ctk.CTkFont(size=12), anchor="w")
            lbl_tipo.pack(side="left", fill="both", expand=True, padx=10)
            
            # Label Status
            lbl_status = ctk.CTkLabel(
                row_frame, 
                text=status_text, 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color=status_color,
                anchor="w"
            )
            lbl_status.pack(side="left", fill="both", expand=True, padx=10)
            
            # Label Data
            lbl_data = ctk.CTkLabel(
                row_frame, 
                text=data_format, 
                font=ctk.CTkFont(size=11), 
                text_color=self.text_muted,
                anchor="w"
            )
            lbl_data.pack(side="left", fill="both", expand=True, padx=10)
            
        # Atualiza rodapé
        self.lbl_page.configure(text=f"Página {self.pagina_atual} de {self.total_paginas}")
        self.lbl_total.configure(text=f"Total: {total_registros} processos")
        
        # Desabilita/habilita botões conforme status
        if self.pagina_atual <= 1:
            self.btn_prev.configure(state="disabled", fg_color="#1e1e1e")
        else:
            self.btn_prev.configure(state="normal", fg_color="#2b2b2b")
            
        if self.pagina_atual >= self.total_paginas:
            self.btn_next.configure(state="disabled", fg_color="#1e1e1e")
        else:
            self.btn_next.configure(state="normal", fg_color="#2b2b2b")
