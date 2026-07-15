# Tasks: Interface Desktop com Plugins para Automação do SEI

**Input**: Design documents from `/specs/001-tkinter-sei-plugin-app/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/plugin-contract.md

**Tests**: Testes unitários de conformidade de carregamento de plugins foram adicionados na fase de polimento para garantir a estabilidade do carregamento modular dinâmico.

**Organization**: As tarefas são agrupadas por ciclo de vida e histórias de usuário (US1, US2, US3) para permitir o desenvolvimento iterativo, testes independentes e entregas incrementais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tarefa executável em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: História de usuário a que pertence a tarefa (US1, US2, US3)
- Caminhos exatos de arquivos estão incluídos nas descrições.

## Path Conventions

- A estrutura do projeto modular de plugins fica concentrada na pasta `src/` no repositório.
- Os arquivos originais de script e .bat legados continuam preservados na raiz do repositório.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização da estrutura de diretórios e validação do ambiente do projeto.

- [X] T001 Criar estrutura física de diretórios em `src/`, `src/core/`, `src/plugins/` e `tests/`
- [X] T002 Verificar arquivos locais de bibliotecas e validar o arquivo de requisitos em `requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura lógica necessária para carregar e controlar os plugins de automação em threads separadas.

**⚠️ CRITICAL**: Nenhuma tela ou história de usuário pode começar até que estes arquivos de infraestrutura básica estejam finalizados.

- [X] T003 Criar o arquivo de contrato e classe abstrata base `src/core/plugin_base.py`
- [X] T004 Criar o gerenciador de descoberta e importação dinâmica de módulos `src/core/plugin_manager.py` usando `importlib`
- [X] T005 Criar o executor de tarefas assíncronas e canalização de logs via fila `src/core/executor.py`

**Checkpoint**: Fundação pronta - a interface gráfica do Tkinter pode agora ser desenvolvida sobre estes módulos.

---

## Phase 3: User Story 1 - Execução de uma Automação do SEI via Interface (Priority: P1) 🎯 MVP

**Goal**: Permitir que o operador selecione um robô disponível, dispare sua execução e acompanhe as mensagens de log em tempo real na tela, recebendo avisos pop-up em caso de falha catastrófica.

**Independent Test**: Executar a UI principal do Tkinter, selecionar um plugin integrado, iniciar a automação e confirmar que os logs são adicionados na área de console rolável sem congelar a janela, e que erros são exibidos em caixas de diálogo pop-up.

### Implementation for User Story 1

- [X] T006 [US1] Desenhar o layout principal da aplicação Tkinter com Combobox, console de logs (ScrolledText) e botões de controle em `src/app.py`
- [X] T007 [US1] Integrar o executor de threads de background `src/core/executor.py` no ciclo de vida de início/fim de execução do app em `src/app.py`
- [X] T008 [US1] Implementar o loop periódico de monitoramento de logs (usando o método `.after()` do Tkinter) para atualizar a tela principal em `src/app.py`
- [X] T009 [US1] Adicionar tratamento de exceções globais com alertas pop-up nativos `messagebox.showerror` para erros críticos de execução do bot em `src/app.py`

**Checkpoint**: O MVP está completo. É possível abrir o app, escolher uma automação padrão e rodá-la com logs em tempo real sem travar a interface.

---

## Phase 4: User Story 2 - Adição Simplificada de Nova Automação / Mecanismo de Plugins (Priority: P2)

**Goal**: Permitir que novas automações definam seus parâmetros de entrada necessários em metadados estruturados e que a UI monte os formulários com os campos de entrada corretos dinamicamente.

**Independent Test**: Criar um arquivo de plugin de testes na pasta `src/plugins/` com parâmetros de texto e booleano e validar se os rótulos e campos de texto e checkboxes correspondentes são desenhados corretamente na tela ao selecionar este plugin.

### Implementation for User Story 2

- [X] T010 [US2] Implementar o gerador dinâmico de formulários e widgets (Entry, Checkbutton) em `src/app.py` mapeados a partir de `plugin.get_params_schema()`
- [X] T011 [US2] Adicionar validação de presença e obrigatoriedade de campos (`is_required`) antes de despachar parâmetros para a thread em `src/app.py`
- [X] T012 [P] [US2] Criar um plugin básico demonstrativo com parâmetros de teste estruturados em `src/plugins/dummy_plugin.py`

**Checkpoint**: A extensão por plugins está operacional. Qualquer desenvolvedor pode adicionar um novo arquivo Python com parâmetros declarados e vê-lo montado na interface.

---

## Phase 5: User Story 3 - Passagem Flexível de Fontes de Dados Externas & Plugins Adaptados (Priority: P3)

**Goal**: Possibilitar a entrada de caminhos de arquivos locais (planilhas, PDFs, pastas) através de diálogos gráficos de seleção e migrar a lógica dos robôs legados para a estrutura de plugins.

**Independent Test**: Selecionar o plugin exportador portado na UI, selecionar uma planilha Excel de entrada através do botão Explorer gráfico nativo, iniciar a automação e verificar se ela lê os dados e realiza o ciclo de exportação no SEI.

### Implementation for User Story 3

- [X] T013 [US3] Adicionar componentes de seleção gráfica de arquivos/pastas (`filedialog.askopenfilename` e `askdirectory`) associados ao gerador dinâmico em `src/app.py`
- [X] T014 [P] [US3] Copiar e adaptar a lógica de automação de processos legada do arquivo `exportador_sei.py` para a classe de plugin em `src/plugins/exportador_sei_plugin.py`
- [X] T015 [P] [US3] Copiar e adaptar a lógica de indexação de arquivos PDFs legada do arquivo `indexador_pdf.py` para a classe de plugin em `src/plugins/indexador_pdf_plugin.py`
- [X] T016 [P] [US3] Copiar e adaptar a lógica de webhook e comunicação legada do arquivo `enviar_n8n.py` para a classe de plugin em `src/plugins/enviar_n8n_plugin.py`

**Checkpoint**: O escopo completo do sistema foi portador para plugins e a interface gráfica do Tkinter suporta todas as entradas dinâmicas de arquivos e planilhas exigidas.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Polimento de segurança do ciclo de vida dos navegadores e validações gerais do projeto.

- [X] T017 [P] Criar testes unitários para a classe de descoberta `PluginManager` em `tests/test_plugin_manager.py`
- [X] T018 Adicionar rotinas de encerramento seguro de navegadores remotos e instâncias do Chrome ativas ao fechar a janela principal da UI em `src/app.py`
- [X] T019 Validar o fluxo de implantação e execução completo contra as instruções de `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências, inicia o projeto.
- **Foundational (Phase 2)**: Depende da estrutura física estabelecida na Fase 1. Bloqueia o desenvolvimento das telas de usuário.
- **User Stories (Phase 3+)**: Todas as histórias dependem da fundação lógica (`plugin_manager.py` e `executor.py`) estar concluída.
  - A **US1** (Mecanismo básico de execução e logs da UI) deve ser desenvolvida em primeiro lugar como núcleo do MVP.
  - A **US2** (Formulários dinâmicos de parâmetros) estende os controles da US1.
  - A **US3** (Seletores de arquivos nativos e robôs adaptados) fornece a massa de dados final para as automações portadas.
- **Polish (Phase N)**: Depende da conclusão de todas as histórias desejadas.

### Parallel Opportunities

- Durante a **Fase 2**: A criação do `plugin_manager.py` (T004) e do `executor.py` (T005) pode ser desenvolvida de forma paralela.
- Durante a **Fase 4**: O plugin de testes dummy (T012) pode ser criado paralelamente à lógica de desenho dinâmico de formulários da UI (T010).
- Durante a **Fase 5**: Os três robôs baseados nas automações antigas (`exportador_sei_plugin.py`, `indexador_pdf_plugin.py` e `enviar_n8n_plugin.py`) podem ser portados e construídos em paralelo por desenvolvedores diferentes (T014, T015 e T016), pois representam arquivos de plugin independentes.

---

## Parallel Example: Phase 5 (Porting Automações)

```bash
# Desenvolvedores diferentes podem programar as automações portadas de forma isolada e simultânea:
Task: "Copiar e adaptar a lógica de exportador_sei.py em src/plugins/exportador_sei_plugin.py"
Task: "Copiar e adaptar a lógica de indexador_pdf.py em src/plugins/indexador_pdf_plugin.py"
Task: "Copiar e adaptar a lógica de enviar_n8n.py em src/plugins/enviar_n8n_plugin.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir a configuração inicial do diretório `src/` (Fase 1).
2. Construir as classes de carregamento dinâmico de plugins e executor de background threads (Fase 2).
3. Construir a interface Tkinter e a rotina de canalização de logs na tela principal (Fase 3 - US1).
4. **VALIDAÇÃO MVP**: Criar manualmente um bot de teste síncrono e certificar-se de que ele roda e exibe logs em tempo real sem travar a interface e que pop-ups de erro são mostrados em falhas.

### Incremental Delivery

1. Com a fundação da interface rodando com logs (MVP), adicionar o gerador dinâmico de widgets para capturar parâmetros (US2).
2. Adicionar o suporte gráfico a seletores de arquivos de planilhas nativos do Windows (US3).
3. Importar a lógica individual dos scripts legados para a pasta de plugins um a um (Exportador -> Indexador -> Enviar N8N), testando e integrando-os na UI de maneira incremental e isolada.
