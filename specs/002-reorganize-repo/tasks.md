# Tasks: Reorganização Física do Repositório

**Input**: Design documents from `/specs/002-reorganize-repo/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/path-contract.md

**Tests**: Testes manuais e unitários locais foram inseridos na fase de polimento para garantir que a migração não quebrou os caminhos do interpretador python e da suite de testes.

**Organization**: As tarefas são organizadas por história de usuário para garantir que o aplicativo Tkinter possa ser movido e testado isoladamente (MVP) antes da movimentação dos scripts adicionais e executáveis `.bat`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tarefa executável em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: História de usuário correspondente (US1, US2, US3)
- Caminhos exatos de arquivos estão incluídos nas descrições.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização da estrutura de diretórios e preparação de ignore do Git.

- [X] T001 Criar os novos diretórios vazios de destino `scripts/` e `bin/` na raiz do projeto
- [X] T002 [P] Atualizar o arquivo `.gitignore` para registrar e ajustar caminhos ignorados das pastas movidas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Movimentação física primária da aplicação Tkinter e suíte de testes.

**⚠️ CRITICAL**: A aplicação não pode ser validada em seu novo diretório até que os arquivos físicos tenham sido movidos.

- [X] T003 Mover o diretório `src/` para o diretório de destino `app/` na raiz do repositório
- [X] T004 Mover o diretório `tests/` para o diretório de destino `app/tests/` na raiz do repositório

**Checkpoint**: Estrutura física da aplicação Tkinter reorganizada.

---

## Phase 3: User Story 1 - Execução Integrada do Aplicativo na Nova Pasta (Priority: P1) 🎯 MVP

**Goal**: Garantir que o aplicativo gráfico Tkinter execute com sucesso em seu novo diretório e todos os imports locais funcionem.

**Independent Test**: Executar a aplicação com `app/app.py` e verificar se a interface inicial renderiza e carrega os plugins dinâmicos da nova pasta `app/plugins/` sem quebras de imports.

### Implementation for User Story 1

- [X] T005 [US1] Atualizar imports absolutos de `src.` para `app.` em todos os arquivos de `app/app.py`, `app/core/` e `app/plugins/`
- [X] T006 [US1] Ajustar no arquivo `app/core/plugin_manager.py` os caminhos dinâmicos do pacote de importação para `app.plugins` e diretório de varredura correspondente
- [X] T007 [US1] Atualizar caminhos absolutos e imports de referências em `app/tests/test_plugin_manager.py`

**Checkpoint**: O MVP está funcional. A aplicação Tkinter e seus plugins executam na pasta `app/` e os testes unitários internos passam com sucesso.

---

## Phase 4: User Story 2 - Execução Isolada de Scripts de Automação Individuais (Priority: P2)

**Goal**: Isolar os scripts de automação individuais/legados em uma pasta própria para testes e novas lógicas de robô sem interferir na aplicação gráfica.

**Independent Test**: Verificar se os scripts legados rodam de forma autônoma a partir de `scripts/` com o interpretador python.

### Implementation for User Story 2

- [X] T008 [US2] Mover os scripts individuais `enviar_n8n.py`, `exportador_sei.py`, `exportador_sei_isoleted.py`, `exportador_sei_isoleted_debug.py` e `indexador_pdf.py` para a nova pasta `scripts/`
- [X] T009 [US2] Inspecionar referências internas a arquivos relativos (como `processos.txt` ou `automacao.db`) nos scripts em `scripts/` e adaptá-los se necessário

**Checkpoint**: Scripts individuais de desenvolvimento e testes isolados com sucesso na pasta `scripts/`.

---

## Phase 5: User Story 3 - Execução de Automações por Arquivos de Lote (.bat) (Priority: P3)

**Goal**: Centralizar arquivos `.bat` em uma pasta executável própria, mantendo a chamada dinâmica para o ambiente virtual `.venv` e scripts.

**Independent Test**: Rodar o executável `bin/iniciar_chrome_debug.bat` e validar se ele dispara o navegador com sucesso.

### Implementation for User Story 3

- [X] T010 [US3] Mover arquivos `.bat` (`iniciar_chrome_debug.bat`, `iniciar_exportador_isolado.bat`, `iniciar_exportador_isolado_debug.bat`, `iniciar_indexador.bat`) da raiz para a nova pasta `bin/`
- [X] T011 [US3] Atualizar a codificação interna de todos os arquivos `.bat` em `bin/` para utilizarem o prefixo `%~dp0..\` dinâmico em suas chamadas

**Checkpoint**: Arquivos `.bat` organizados em `bin/` e totalmente operacionais com caminhos relativos e portáveis.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Verificações de integridade, testes automatizados e atualização de documentação.

- [X] T012 Executar e passar todos os testes unitários locais com o comando `.\.venv\Scripts\python.exe -m unittest app/tests/test_plugin_manager.py`
- [X] T013 [P] Executar e validar a inicialização do Chrome e do exportador em lote diretamente da pasta `bin/`
- [X] T014 Atualizar a documentação do repositório no arquivo `README.md` com as novas instruções e layouts físicos

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências, inicia o workflow.
- **Foundational (Phase 2)**: Depende da criação do layout. Bloqueia a codificação de imports do app.
- **User Stories (Phase 3+)**:
  * A **US1** (Integração e imports do app) depende diretamente da conclusão física da Fase 2.
  * A **US2** (Portabilidade dos scripts isolados) e a **US3** (Executáveis `.bat` em `bin/`) podem ser executadas paralelamente após a conclusão da US1, pois não tocam nos mesmos arquivos do aplicativo Tkinter.
- **Polish (Phase N)**: Depende do término de todas as US.

### Parallel Opportunities

- Durante a **Fase 1**: A atualização de ignore do git (T002) pode ser feita paralela à criação física dos novos diretórios (T001).
- As Fases **US2** (T008, T009) e **US3** (T010, T011) podem ser executadas de forma paralela por desenvolvedores diferentes após a conclusão do MVP (US1).
- Na fase de **Polimento**: O teste manual do atalho bat (T013) pode ser executado em paralelo ao teste unitário da aplicação (T012).

---

## Parallel Example: Fases US2 e US3

```bash
# Um desenvolvedor pode portar os scripts de automação isolados enquanto outro atualiza os arquivos .bat em bin/
Task: "Mover os scripts individuais da raiz para a nova pasta scripts/ e validar imports"
Task: "Mover os arquivos .bat para a nova pasta bin/ e atualizar variáveis %~dp0"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir a criação de diretórios vazios na Fase 1.
2. Mover a pasta antiga `src/` e `tests/` para suas novas posições `app/` e `app/tests/` na Fase 2.
3. Atualizar e corrigir todos os imports quebrados de `src.` para `app.` nos arquivos python em `app/` (Fase 3 - US1).
4. **VALIDAÇÃO MVP**: Executar a suite de testes unitários em `app/tests/test_plugin_manager.py` e rodar a interface em `app/app.py` para atestar a estabilidade.

### Incremental Delivery

1. Com a UI funcionando, mover os scripts legados para `scripts/` (US2) e testar a invocação direta pelo terminal.
2. Mover os arquivos `.bat` para `bin/` (US3) e atualizar para `%~dp0..\`, testando as chamadas em lote.
3. Testar a integridade global e documentar (Fase N).
