import customtkinter as ctk

class LogViewer(ctk.CTkFrame):
    """
    Componente console para exibição dinâmica de logs em tempo real com auto-scroll.
    """
    def __init__(self, master, max_lines=150, **kwargs):
        super().__init__(master, **kwargs)
        
        self.max_lines = max_lines
        self.linhas_atuais = 0
        
        self.configure(fg_color="transparent")
        
        self.criar_cabecalho()
        self.criar_console()

    def criar_cabecalho(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))
        
        lbl = ctk.CTkLabel(
            header,
            text="Console de Execução em Tempo Real",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1f538d"
        )
        lbl.pack(side="left")
        
        btn_limpar = ctk.CTkButton(
            header,
            text="Limpar Console",
            width=90,
            height=24,
            fg_color="#3a3a3a",
            hover_color="#4f4f4f",
            corner_radius=4,
            command=self.limpar_logs
        )
        btn_limpar.pack(side="right")

    def criar_console(self):
        # Caixa de texto de log com visual de terminal escuro
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color="#0e0e0e",
            text_color="#39ff14", # Verde neon estilo terminal
            font=ctk.CTkFont(family="Courier", size=12),
            border_color="#222222",
            border_width=1,
            corner_radius=6,
            activate_scrollbars=True
        )
        self.textbox.pack(fill="both", expand=True)
        self.textbox.configure(state="disabled")

    def adicionar_log(self, mensagem: str):
        """
        Adiciona uma nova linha de log e aplica autoscroll.
        Mete um limite de linhas para manter a performance estável.
        """
        self.textbox.configure(state="normal")
        
        # Insere a nova linha
        self.textbox.insert("end", f"{mensagem}\n")
        self.linhas_atuais += 1
        
        # Se ultrapassar o limite, apaga a primeira linha
        if self.linhas_atuais > self.max_lines:
            self.textbox.delete("1.0", "2.0")
            self.linhas_atuais -= 1
            
        # Garante foco no final (autoscroll)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def limpar_logs(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.linhas_atuais = 0
        self.textbox.configure(state="disabled")
