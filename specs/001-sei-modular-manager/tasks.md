# Tasks: Gerenciador de Automações SEI Modular

**Input**: Design documents from `/specs/001-sei-modular-manager/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Testes incluídos nas fases de tarefas para validação robusta de cada User Story (são recomendados testes unitários e de integração para garantir o desacoplamento e bom funcionamento da arquitetura).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `core/`, `procedures/`, `ui/`, `tests/` at repository root
- Paths below respect the project structure described in `plan.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Criar a estrutura básica de diretórios e arquivos vazios em `core/`, `procedures/`, `ui/components/`, `tests/` e na raiz do repositório
- [X] T002 Configurar dependências necessárias no arquivo `requirements.txt`
- [X] T003 [P] Configurar variáveis de ambiente e valores de teste no arquivo `.env`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Definir a classe de base abstrata de procedimento `BaseProcedure` em `core/base_procedure.py`
- [X] T005 [P] Implementar extrator e manipulador básico de arquivos PDF em `core/pdf_processor.py`
- [X] T006 [P] Configurar conexão SQLite e inicialização do banco local de dados em `core/database.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Persistência de Dados e Consulta de Processos (Priority: P1) 🎯 MVP

**Goal**: Persistir dados de processos no SQLite e expor consultas com busca textual e paginação otimizadas.

**Independent Test**: Executar consultas no banco SQLite local e validar que as cláusulas `LIMIT` e `OFFSET` retornam apenas a página solicitada, funcionando com termos de busca e filtros de status.

### Implementation for User Story 1

- [X] T007 [P] [US1] Criar tabela de processos e métodos de inserção/carga de sementes (seeding) em `core/database.py`
- [X] T008 [US1] Implementar a função `obter_processos_paginados(pagina, itens_por_pagina, filtro_status, busca)` utilizando LIMIT/OFFSET em `core/database.py`
- [X] T009 [US1] Implementar testes unitários para inserção, paginação e buscas em `tests/test_database.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Execução e Registro de Procedimentos Modulares (Priority: P2)

**Goal**: Registrar e descobrir dinamicamente na inicialização do app qualquer procedimento que herde de BaseProcedure na pasta `procedures/`.

**Independent Test**: Adicionar um procedimento de teste dummy na pasta `procedures/`, incluí-lo no `__init__.py` e verificar se a orquestração backend o detecta e lê suas configurações dinamicamente.

### Implementation for User Story 2

- [X] T010 [P] [US2] Implementar procedimento de exemplo herdando de BaseProcedure em `procedures/exportador_sei.py`
- [X] T011 [US2] Criar sistema de importação automática e registro dinâmico no `__init__.py` do pacote `procedures/`
- [X] T012 [US2] Escrever testes de descoberta e validação do ciclo de vida das instâncias de procedimentos em `tests/test_procedures.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Interface de Usuário Paginada e Responsiva (Priority: P3)

**Goal**: Construir a interface CustomTkinter com tabela paginada, buscas, configurações e console de logs assíncrono via threads.

**Independent Test**: Abrir o aplicativo UI, interagir com a paginação da tabela, executar uma automação de teste e checar se a tela continua responsiva a cliques enquanto os logs sobem na caixa de texto.

### Implementation for User Story 3

- [X] T013 [P] [US3] Desenvolver componente de tabela paginada com botões Anterior/Próximo e busca debounced em `ui/components/paginated_table.py`
- [X] T014 [P] [US3] Desenvolver componente console para exibição de logs em tempo real em `ui/components/log_viewer.py`
- [X] T015 [US3] Implementar o gerenciador da tela principal CustomTkinter e orquestração de threads em `ui/app.py`
- [X] T016 [US3] Implementar a renderização dinâmica de formulários na UI baseada em `fixed_settings` e `variable_settings` do procedimento selecionado em `ui/app.py`
- [X] T017 [US3] Criar o arquivo orquestrador de entrada `main.py` para instanciar a UI e conectá-la aos controladores do backend

**Checkpoint**: User Stories 1, 2, and 3 should now be independently functional and integrated

---

## Phase 6: User Story 4 - Integração Genérica de IA via n8n (Priority: P4)

**Goal**: Criar cliente genérico e desacoplado para enviar prompts e arquivos para o webhook n8n via requisições HTTP multipart POST.

**Independent Test**: Executar testes chamando a função de envio, mockando a resposta HTTP do webhook n8n, e validar a formatação do retorno.

### Implementation for User Story 4

- [X] T018 [P] [US4] Implementar a função `enviar_para_ia(webhook_url, arquivo_path, prompt)` usando a biblioteca `requests` em `core/n8n_client.py`
- [X] T019 [US4] Adicionar tratamento de erros de conexão, timeouts e decodificação estruturada de dicionário/JSON em `core/n8n_client.py`
- [X] T020 [US4] Desenvolver testes de integração com chamadas de rede mockadas em `tests/test_n8n_client.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T021 Criar arquivos batch de inicialização rápida na raiz do projeto (ex: `.bat` para Windows)
- [X] T022 Documentar o processo de execução e guias no arquivo `README.md`
- [X] T023 Validar a aderência completa ao guia de início rápido executando toda a suíte de testes com `pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências - inicia imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão do Setup - BLOQUEIA todas as histórias de usuários.
- **User Stories (Phase 3+)**: Todas dependem da conclusão da fase Fundacional (Phase 2).
  - As histórias podem ser desenvolvidas sequencialmente (P1 -> P2 -> P3 -> P4) para validações de MVP contínuas.
  - Alternativamente, as tarefas paralelas dentro de histórias independentes podem rodar concorrentemente.
- **Polish (Final Phase)**: Depende do término de todas as histórias desejadas.

### Parallel Opportunities

- Tarefas T001, T002, T003 da Phase 1 podem ser estruturadas rapidamente em paralelo.
- Tarefas Fundacionais T005 e T006 podem rodar paralelamente (arquivos e banco).
- Uma vez concluída a Phase 2 (Foundational):
  - A equipe pode dividir o desenvolvimento de histórias paralelas: enquanto um foca na persistência de dados (US1), outro pode configurar o cliente n8n (US4) e outro o exemplo de exportador (US2).
- Os componentes de UI `paginated_table.py` (T013) e `log_viewer.py` (T014) podem ser desenvolvidos em paralelo por programadores diferentes antes da integração no controlador da UI (T015).

---

## Parallel Example: User Story 3

```bash
# Desenvolvedores trabalhando em componentes visuais independentes:
Task: "Desenvolver tabela paginada em ui/components/paginated_table.py"
Task: "Desenvolver console de logs em ui/components/log_viewer.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2 Only)

1. Concluir Setup (Fase 1) e Fundações (Fase 2).
2. Implementar a persistência SQLite e sua paginação (Fase 3 - US1).
3. Implementar a descoberta e o procedimento de exemplo (Fase 4 - US2).
4. **VALIDAÇÃO**: Garantir que o banco de dados carregue processos e os plugins sejam listados no backend sem erros.
5. Iniciar UI básica (Fase 5 - US3) para testar visualmente.
