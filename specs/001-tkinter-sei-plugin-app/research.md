# Research & Decisions: Interface Desktop com Plugins para Automação do SEI

Este documento registra as principais decisões de design técnico, arquitetura e usabilidade tomadas após pesquisa das necessidades do projeto e restrições técnicas.

## Decisão 1: Mecanismo de Carregamento Dinâmico de Plugins

### Contexto
Para evitar acoplamento rígido entre a interface gráfica (Tkinter) e as automações (bots), é necessário que novas automações possam ser incluídas simplesmente adicionando um arquivo em uma pasta, sem que o código da UI saiba previamente da sua existência.

### Escolha
Carregamento dinâmico via introspecção de arquivos com `importlib` e classe base abstrata.

### Rationale
- O Python possui o módulo nativo `importlib` que permite importar arquivos dinamicamente em tempo de execução.
- Definiremos uma classe base abstrata `BasePlugin` da qual todos os robôs herdarão.
- Ao iniciar, o gerenciador de plugins (`PluginManager`) irá varrer a pasta `src/plugins/`, importar todos os módulos Python nela contidos, instanciar as subclasses de `BasePlugin` e registrá-las no sistema.

### Alternativas Consideradas
- **Registro em arquivo JSON de configuração**: Requerer que o desenvolvedor edite um arquivo de texto `config.json` para declarar o novo plugin. Rejeitado porque quebra o princípio de plugin "plug-and-play" e aumenta o risco de erros de digitação.

---

## Decisão 2: Geração Dinâmica de Formulários em Tkinter

### Contexto
Como cada plugin pode exigir entradas de dados totalmente diferentes (ex: uma senha, uma planilha de processos, um diretório de arquivos, flags booleanas), a UI do Tkinter precisa renderizar um formulário dinamicamente que se ajuste a essas necessidades sem codificação rígida.

### Escolha
Especificação declarativa de parâmetros nos metadados do plugin e mapeamento dinâmico de widgets.

### Rationale
- Cada classe de plugin definirá um método ou propriedade estática `get_params_schema()` que retorna uma lista de dicionários especificando seus parâmetros:
  ```python
  def get_params_schema(self):
      return [
          {"name": "url_sei", "type": "text", "label": "URL do SEI", "default": "http://..."},
          {"name": "input_file", "type": "file", "label": "Planilha de Processos", "extensions": [".xlsx", ".csv"]}
      ]
  ```
- O módulo da UI terá um construtor de formulários que itera sobre esse esquema e renderiza dinamicamente:
  - `type == "text"` -> `ttk.Label` + `ttk.Entry`
  - `type == "file"` -> `ttk.Label` + `ttk.Entry` + `ttk.Button` (que abre `filedialog.askopenfilename`)
  - `type == "directory"` -> `ttk.Label` + `ttk.Entry` + `ttk.Button` (que abre `filedialog.askdirectory`)
  - `type == "bool"` -> `ttk.Checkbutton`

### Alternativas Consideradas
- **Telas Tkinter customizadas por plugin**: Permitir que cada plugin desenhasse sua própria seção na UI. Rejeitado porque expõe o desenvolvedor de robôs ao desenvolvimento direto em Tkinter, aumentando a complexidade e reduzindo a padronização visual da aplicação.

---

## Decisão 3: Concorrência e Thread-Safety com Tkinter

### Contexto
Automações Web (Selenium, Playwright) são operações de longa duração. Se executadas diretamente na thread do Tkinter, a UI travará (congelará) imediatamente, impedindo o usuário de ver logs ou cancelar a execução. Porém, atualizar elementos de UI a partir de outra thread secundária é inseguro e gera falhas aleatórias no Tkinter.

### Escolha
Execução em `threading.Thread` secundária com passagem de progresso por fila de mensagens (`queue.Queue`) consumida na thread principal através do método `.after()` do Tkinter.

### Rationale
- Cada execução de plugin roda em uma thread dedicada.
- O plugin recebe um objeto de log que enfileira mensagens em uma fila segura (`queue.Queue`).
- A UI do Tkinter monitora essa fila periodicamente (ex: a cada 100ms usando `root.after(100, update_log_widget)`) para extrair e exibir novas mensagens na caixa de logs da tela sem corromper o estado do loop do Tkinter.

### Alternativas Consideradas
- **Bibliotecas assíncronas (asyncio)**: Utilizar Loop do Playwright integrado ao loop do Tkinter. Rejeitado devido à complexidade de integrar loops de eventos de asyncio com o mainloop do Tkinter em aplicações desktop, que costuma apresentar comportamentos imprevisíveis em plataformas Windows.

---

## Decisão 4: Preservação dos Scripts Legados e .bat

### Contexto
O usuário solicitou explicitamente que os scripts legados (`enviar_n8n.py`, `exportador_sei.py` e `indexador_pdf.py`) sejam mantidos junto aos seus arquivos `.bat` na raiz do repositório para permitir execução manual isolada via linha de comando ou tarefas agendadas do Windows.

### Escolha
Manutenção inalterada dos arquivos legados na raiz e criação de uma nova estrutura em `src/` que duplica a lógica de processamento em formato de plugins modulares.

### Rationale
- Evita quebras em pipelines ou agendamentos locais existentes executados de fora da aplicação gráfica.
- Permite refatorar as automações nos plugins de forma modular, adotando a classe base de plugins sem se preocupar em quebrar a retrocompatibilidade da interface de CLI ou de arquivos de configuração dos scripts antigos.
