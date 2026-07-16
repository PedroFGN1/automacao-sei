import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Garante que o diretório raiz esteja no sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.plugin_manager import PluginManager
from app.core.executor import PluginExecutor

class SEIAutomationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto SEI")
        self.root.geometry("800x650")
        self.root.minsize(700, 500)
        
        # Cores e Estilos (Design Clean e Moderno)
        self.bg_color = "#f4f6f9"
        self.card_color = "#ffffff"
        self.primary_color = "#2b579a"  # Azul corporativo SEI
        self.accent_color = "#2ecc71"   # Verde para Iniciar
        self.stop_color = "#e74c3c"     # Vermelho para Parar
        self.text_dark = "#2c3e50"
        self.terminal_bg = "#1e1e1e"
        self.terminal_fg = "#d4d4d4"
        
        self.root.configure(bg=self.bg_color)
        
        # Configuração de Estilo do ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=self.bg_color, foreground=self.text_dark)
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.primary_color)
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 11, "bold"), foreground=self.text_dark)
        self.style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=0)
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        
        # Inicializa Gerenciador de Plugins
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.current_executor = None
        
        # Construção da Interface
        self.create_widgets()
        self.populate_plugins()
        
    def create_widgets(self):
        # 1. CABEÇALHO (Header)
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame, 
            text="SEI Automation Hub", 
            font=("Segoe UI", 16, "bold"), 
            bg=self.primary_color, 
            fg="#ffffff"
        )
        header_label.pack(side="left", padx=20, pady=12)
        
        version_label = tk.Label(
            header_frame, 
            text="v1.0.0", 
            font=("Segoe UI", 9), 
            bg=self.primary_color, 
            fg="#a5c4f2"
        )
        version_label.pack(side="right", padx=20, pady=18)
        
        # Container Principal com padding
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 2. CARTÃO DE CONFIGURAÇÃO DO ROBÔ
        self.config_card = ttk.Frame(main_container, style="Card.TFrame")
        self.config_card.pack(fill="x", side="top", pady=(0, 10))
        
        # Padding interno para o cartão
        inner_config = tk.Frame(self.config_card, bg=self.card_color, padx=15, pady=15)
        inner_config.pack(fill="both", expand=True)
        
        # Seleção de Robô
        ttk.Label(inner_config, text="Selecione a Automação:", style="Subheader.TLabel", background=self.card_color).grid(row=0, column=0, sticky="w", pady=5)
        
        self.plugin_var = tk.StringVar()
        self.plugin_combo = ttk.Combobox(inner_config, textvariable=self.plugin_var, state="readonly", width=45, font=("Segoe UI", 10))
        self.plugin_combo.grid(row=1, column=0, sticky="we", pady=5, padx=(0, 15))
        self.plugin_combo.bind("<<ComboboxSelected>>", self.on_plugin_selected)
        
        # Opções Globais (Modo de Exibição / Headless)
        options_frame = tk.Frame(inner_config, bg=self.card_color)
        options_frame.grid(row=0, column=1, rowspan=2, sticky="nswe")
        
        self.headless_var = tk.BooleanVar(value=False)  # Padrão: Modo Visível (headless=False)
        self.headless_chk = tk.Checkbutton(
            options_frame, 
            text="Executar em segundo plano (Oculto)", 
            variable=self.headless_var,
            bg=self.card_color,
            activebackground=self.card_color,
            fg=self.text_dark,
            font=("Segoe UI", 10)
        )
        self.headless_chk.pack(anchor="w", pady=5)
        
        # Grid weights
        inner_config.columnconfigure(0, weight=2)
        inner_config.columnconfigure(1, weight=1)
        
        # 3. PAINEL DINÂMICO DE PARÂMETROS
        self.params_card = ttk.Frame(main_container, style="Card.TFrame")
        self.params_card.pack(fill="both", expand=True, pady=10)
        
        self.inner_params = tk.Frame(self.params_card, bg=self.card_color, padx=15, pady=15)
        self.inner_params.pack(fill="both", expand=True)
        
        self.params_title = ttk.Label(self.inner_params, text="Configurações do Robô", style="Subheader.TLabel", background=self.card_color)
        self.params_title.pack(anchor="w", pady=(0, 10))
        
        self.params_form_frame = tk.Frame(self.inner_params, bg=self.card_color)
        self.params_form_frame.pack(fill="both", expand=True)
        
        # Mensagem inicial se nenhum plugin selecionado
        self.placeholder_label = tk.Label(
            self.params_form_frame, 
            text="Selecione um robô acima para visualizar e preencher seus parâmetros.", 
            font=("Segoe UI Light", 11), 
            fg="#7f8c8d", 
            bg=self.card_color
        )
        self.placeholder_label.pack(pady=40)
        
        # Dicionário para armazenar referências das Tkinter Variables dos campos de entrada
        self.param_widgets_vars = {}
        
        # 4. PAINEL DE CONTROLE E LOGS
        bottom_frame = tk.Frame(main_container, bg=self.bg_color)
        bottom_frame.pack(fill="both", expand=True, side="bottom", pady=(10, 0))
        
        # Botões de Ação
        actions_frame = tk.Frame(bottom_frame, bg=self.bg_color)
        actions_frame.pack(fill="x", side="top", pady=(0, 5))
        
        self.btn_start = tk.Button(
            actions_frame, 
            text="Iniciar Automação", 
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color, 
            fg="#ffffff", 
            activebackground="#27ae60",
            activeforeground="#ffffff",
            relief="flat", 
            padx=20, 
            pady=6,
            command=self.start_automation
        )
        self.btn_start.pack(side="left")
        
        self.status_indicator = tk.Label(
            actions_frame, 
            text="Status: Pronto", 
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        self.status_indicator.pack(side="right", pady=8)
        
        # Console de Logs (Terminal)
        logs_label = ttk.Label(bottom_frame, text="Console de Execução:", style="Subheader.TLabel")
        logs_label.pack(anchor="w", pady=(5, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            bottom_frame, 
            bg=self.terminal_bg, 
            fg=self.terminal_fg,
            insertbackground="#ffffff", # cursor branco
            font=("Consolas", 10), 
            height=12
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled") # Somente leitura por padrão
        
    def populate_plugins(self):
        """Popula o combobox com a lista de robôs carregados."""
        plugins = self.plugin_manager.list_plugins()
        plugin_names = [f"{p.name} ({p.id})" for p in plugins]
        self.plugin_combo["values"] = plugin_names
        
        if not plugin_names:
            self.plugin_combo.set("Nenhum robô encontrado")
            self.btn_start.config(state="disabled")
            
    def on_plugin_selected(self, event=None):
        """Disparado quando o usuário seleciona um robô no combobox."""
        selected_text = self.plugin_var.get()
        if not selected_text or selected_text == "Nenhum robô encontrado":
            return
            
        # Extrai o ID do plugin do texto (formato "Nome (id)")
        plugin_id = selected_text.split("(")[-1].replace(")", "").strip()
        plugin = self.plugin_manager.get_plugin(plugin_id)
        
        if plugin:
            self.build_params_form(plugin)
            
    def build_params_form(self, plugin):
        """Constrói dinamicamente os widgets do formulário baseado no schema do plugin."""
        # Limpa widgets anteriores
        for widget in self.params_form_frame.winfo_children():
            widget.destroy()
            
        self.param_widgets_vars.clear()
        self.placeholder_label = None
        
        schema = plugin.get_params_schema()
        if not schema:
            no_params_lbl = tk.Label(
                self.params_form_frame, 
                text="Este robô não exige parâmetros de entrada adicionais.", 
                font=("Segoe UI", 10, "italic"), 
                fg="#7f8c8d", 
                bg=self.card_color
            )
            no_params_lbl.pack(pady=20)
            return

        # Container interno com grid para alinhar rótulos e widgets
        form_grid = tk.Frame(self.params_form_frame, bg=self.card_color)
        form_grid.pack(fill="x", anchor="n")
        form_grid.columnconfigure(1, weight=1)
        
        for idx, param in enumerate(schema):
            name = param["name"]
            label_text = param["label"]
            param_type = param["type"]
            is_required = param.get("is_required", False)
            default = param.get("default_value", "")
            
            # Adiciona asterisco se o parâmetro for obrigatório
            display_label = f"{label_text}:"
            if is_required:
                display_label = f"{label_text} *:"
                
            lbl = tk.Label(
                form_grid, 
                text=display_label, 
                font=("Segoe UI", 10), 
                bg=self.card_color, 
                fg=self.text_dark,
                anchor="w"
            )
            lbl.grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=6)
            
            # Cria a variável correspondente ao tipo de entrada
            if param_type == "bool":
                var = tk.BooleanVar(value=bool(default))
                widget = tk.Checkbutton(
                    form_grid, 
                    variable=var, 
                    bg=self.card_color, 
                    activebackground=self.card_color
                )
                widget.grid(row=idx, column=1, sticky="w", pady=6)
            elif param_type == "password":
                var = tk.StringVar(value=str(default))
                widget = ttk.Entry(form_grid, textvariable=var, show="*", font=("Segoe UI", 10))
                widget.grid(row=idx, column=1, sticky="we", pady=6)
            elif param_type in ("file", "directory"):
                var = tk.StringVar(value=str(default))
                
                # Frame horizontal para a caixa de texto e o botão de explorer
                file_frame = tk.Frame(form_grid, bg=self.card_color)
                file_frame.grid(row=idx, column=1, sticky="we", pady=6)
                file_frame.columnconfigure(0, weight=1)
                
                entry = ttk.Entry(file_frame, textvariable=var, font=("Segoe UI", 10))
                entry.grid(row=0, column=0, sticky="we", padx=(0, 5))
                
                # Callback do botão Explorer
                def browse(target_var=var, p_type=param_type, ext=param.get("allowed_extensions", [])):
                    from tkinter import filedialog
                    if p_type == "file":
                        filetypes = []
                        if ext:
                            filetypes.append(("Arquivos compatíveis", " ".join(f"*{e}" for e in ext)))
                        filetypes.append(("Todos os arquivos", "*.*"))
                        
                        path = filedialog.askopenfilename(filetypes=filetypes)
                    else:
                        path = filedialog.askdirectory()
                        
                    if path:
                        target_var.set(os.path.normpath(path))
                
                btn_browse = ttk.Button(file_frame, text="Buscar...", width=10, command=browse)
                btn_browse.grid(row=0, column=1, sticky="e")
            else:  # 'text'
                var = tk.StringVar(value=str(default))
                widget = ttk.Entry(form_grid, textvariable=var, font=("Segoe UI", 10))
                widget.grid(row=idx, column=1, sticky="we", pady=6)
                
            self.param_widgets_vars[name] = (var, param_type, is_required, label_text)
            
    def write_log(self, message: str, level: str = "INFO"):
        """Escreve uma linha de log formatada na caixa do console."""
        self.log_text.config(state="normal")
        time_str = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{time_str}] [{level}] "
        
        # Insere a mensagem
        self.log_text.insert(tk.END, prefix)
        self.log_text.insert(tk.END, f"{message}\n")
        
        # Rola o scroll para o final
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
    def clear_logs(self):
        """Limpa todo o conteúdo do console."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
    def get_form_params(self) -> dict:
        """Coleta e valida os parâmetros do formulário."""
        params = {}
        for name, (var, param_type, is_required, label_text) in self.param_widgets_vars.items():
            val = var.get()
            
            # Validação de obrigatórios
            if is_required:
                if param_type == "bool" and not val:
                    # Booleano falso é permitido se não for obrigatório ter que marcar True.
                    # Mas de modo geral tratamos String vazia como erro.
                    pass
                elif isinstance(val, str) and not val.strip():
                    raise ValueError(f"O parâmetro '{label_text}' é obrigatório.")
                    
            if isinstance(val, str):
                val = val.strip()
            params[name] = val
            
        # Injeta o parâmetro global de headless
        params["headless"] = self.headless_var.get()
        return params
        
    def start_automation(self):
        """Inicia o executor do plugin selecionado em segundo plano."""
        selected_text = self.plugin_var.get()
        if not selected_text or selected_text == "Nenhum robô encontrado":
            messagebox.showwarning("Aviso", "Nenhum robô selecionado para executar.")
            return
            
        plugin_id = selected_text.split("(")[-1].replace(")", "").strip()
        plugin = self.plugin_manager.get_plugin(plugin_id)
        
        if not plugin:
            messagebox.showerror("Erro", "Não foi possível carregar o plugin selecionado.")
            return
            
        try:
            params = self.get_form_params()
        except ValueError as err:
            messagebox.showwarning("Parâmetro Inválido", str(err))
            return
            
        # Limpa console e prepara a UI para rodar
        self.clear_logs()
        self.write_log(f"Iniciando o robô '{plugin.name}'...", "INFO")
        self.set_ui_running_state(True)
        
        # Cria e inicia o executor
        self.current_executor = PluginExecutor(plugin, params)
        self.current_executor.start(on_finish=self.on_automation_finished)
        
        # Agenda o primeiro monitoramento de logs
        self.root.after(100, self.monitor_logs)
        
    def monitor_logs(self):
        """Monitora periodicamente a fila de logs do executor."""
        if not self.current_executor:
            return
            
        # Extrai logs pendentes e exibe na UI
        logs = self.current_executor.get_logs()
        for _, level, msg in logs:
            self.write_log(msg, level)
            
        # Continua monitorando enquanto o robô estiver executando
        if self.current_executor.is_running:
            self.root.after(100, self.monitor_logs)
            
    def on_automation_finished(self, result, error):
        """Callback executado quando a thread do robô termina."""
        # Garante que as últimas mensagens de log pendentes na fila sejam coletadas
        self.root.after(10, self.flush_final_logs)
        
        def handle_ui():
            self.set_ui_running_state(False)
            if error:
                self.status_indicator.config(text="Status: Erro", fg=self.stop_color)
                # Exibe pop-up de diálogo de erro nativo (FR-009)
                messagebox.showerror("Erro na Execução", f"Ocorreu um erro fatal durante a automação:\n\n{str(error)}")
            else:
                self.status_indicator.config(text="Status: Concluído", fg=self.accent_color)
                messagebox.showinfo("Sucesso", f"Automação '{self.current_executor.plugin.name}' finalizada com sucesso!")
                
        # Garante a atualização da UI na thread principal do Tkinter
        self.root.after(0, handle_ui)
        
    def flush_final_logs(self):
        """Coleta as últimas mensagens remanescentes da fila após o término."""
        if self.current_executor:
            logs = self.current_executor.get_logs()
            for _, level, msg in logs:
                self.write_log(msg, level)
                
    def set_ui_running_state(self, is_running: bool):
        """Habilita ou desabilita widgets do formulário de acordo com a execução."""
        state = "disabled" if is_running else "normal"
        combo_state = "disabled" if is_running else "readonly"
        
        # Controles
        self.plugin_combo.config(state=combo_state)
        self.headless_chk.config(state=state)
        
        # Desabilita botões e campos de entrada dinâmicos
        for child in self.params_form_frame.winfo_children():
            self.disable_all_children(child, state)
            
        if is_running:
            self.btn_start.config(text="Executando...", bg="#95a5a6", state="disabled")
            self.status_indicator.config(text="Status: Executando", fg=self.primary_color)
        else:
            self.btn_start.config(text="Iniciar Automação", bg=self.accent_color, state="normal")
            self.status_indicator.config(text="Status: Pronto", fg="#7f8c8d")
            
    def disable_all_children(self, parent, state):
        """Função recursiva para desabilitar/habilitar todos os filhos de um widget."""
        try:
            parent.config(state=state)
        except tk.TclError:
            pass
            
        for child in parent.winfo_children():
            self.disable_all_children(child, state)

if __name__ == "__main__":
    window = tk.Tk()
    app = SEIAutomationApp(window)
    
    # Executa rotina de fechamento seguro ao fechar a janela (T018 de Polish)
    def on_closing():
        if app.current_executor and app.current_executor.is_running:
            if not messagebox.askyesno("Aviso", "Há uma automação ativa rodando em segundo plano. Deseja realmente fechar e interromper os processos do robô?"):
                return
        window.destroy()
        
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()
