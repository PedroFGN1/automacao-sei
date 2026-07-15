# Feature Specification: Gerenciador de Automações SEI Modular

**Feature Branch**: `001-sei-modular-manager`

**Created**: 2026-07-15

**Status**: Draft

**Input**: User description: "Arquivo spec.md original que define a arquitetura e os requisitos técnicos do Gerenciador de Automações SEI Modular desacoplado e extensível"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistência de Dados e Consulta de Processos (Priority: P1)

Como usuário ou operador do sistema, eu preciso carregar a lista de processos armazenados localmente e filtrá-los de forma paginada para que a interface de usuário exiba grandes volumes de dados de maneira rápida e responsiva.

**Why this priority**: A persistência e o carregamento paginado dos processos no banco SQLite (`automacao.db`) representam a base de dados em que todas as automações e telas se apoiam.

**Independent Test**: Pode ser testado executando buscas e consultas SQL parametrizadas diretamente no módulo de banco de dados (`core/database.py`) usando cláusulas `LIMIT` e `OFFSET` para garantir que apenas o subconjunto de registros solicitados seja recuperado da memória.

**Acceptance Scenarios**:

1. **Given** um banco local contendo 100 registros de processos, **When** o sistema solicita a página 3 com limite de 10 itens por página, **Then** o retorno do banco de dados deve conter exatamente 10 registros, correspondendo aos registros da posição 21 a 30.
2. **Given** um usuário buscando por termos específicos como "Portaria", **When** o filtro de busca for ativado, **Then** o sistema deve aplicar buscas textuais com paginação e retornar apenas processos cujos metadados correspondam ao termo procurado.

---

### User Story 2 - Execução e Registro de Procedimentos Modulares (Priority: P2)

Como desenvolvedor de automações, eu preciso herdar de uma classe base abstrata comum para criar novos fluxos independentes de automação (como o `exportador_sei.py`), de forma que o sistema os detecte e configure dinamicamente na interface de usuário.

**Why this priority**: Esta modularidade permite expandir o sistema com novos procedimentos de automação (plugins) sem a necessidade de reescrever o núcleo ou a interface visual, respeitando o princípio de responsabilidade única.

**Independent Test**: Criar um arquivo de automação dummy em `procedures/` herdando de `BaseProcedure`, verificar se o carregamento dinâmico no `__init__.py` detecta suas configurações estáticas/dinâmicas e se a sua execução via método `run()` envia logs de progresso via callback.

**Acceptance Scenarios**:

1. **Given** um novo procedimento de automação criado em `procedures/` que implementa a interface `BaseProcedure`, **When** o sistema inicializa, **Then** o módulo de orquestração deve detectar a nova automação e carregar suas propriedades estáticas (`fixed_settings`) e dinâmicas (`variable_settings`).
2. **Given** um procedimento em execução, **When** ele invoca o método de callback fornecido para logs, **Then** a mensagem de log deve ser despachada imediatamente com o nível e texto correspondentes.

---

### User Story 3 - Interface de Usuário Paginada e Responsiva (Priority: P3)

Como usuário final do sistema, eu preciso interagir com uma janela desktop para buscar processos, configurar automações dinamicamente e executá-las em plano de fundo sem travar a interface e vendo logs em tempo real.

**Why this priority**: Garante uma experiência de uso premium, impedindo que a aplicação desktop fique congelada ou marcada como "não respondendo" durante automações longas de Playwright ou manipulação de PDFs.

**Independent Test**: Executar a interface gráfica CustomTkinter, disparar a execução de uma automação que dura alguns segundos e verificar se a janela continua respondendo a cliques e se a caixa de texto de logs exibe as novas linhas enviadas.

**Acceptance Scenarios**:

1. **Given** uma automação iniciada pelo usuário a partir da tela de execução, **When** o processo for disparado, **Then** o sistema deve iniciar o método `run()` em uma thread dedicada (`threading.Thread`), mantendo a UI totalmente responsiva.
2. **Given** a exibição de logs na interface de usuário, **When** novas mensagens de log são geradas pelo procedimento em execução, **Then** a caixa de texto na UI deve ser atualizada em tempo real via callback, exibindo no máximo as últimas N linhas configuradas.
3. **Given** a tabela de visualização de processos na interface, **When** o usuário clica em "Próximo" ou "Anterior", **Then** a UI deve solicitar a página correspondente ao backend e atualizar os registros da tabela com os novos dados em menos de 0.5 segundos.

---

### User Story 4 - Integração Genérica de IA via n8n (Priority: P4)

Como desenvolvedor de automações, eu preciso de um serviço de comunicação isolado que envie arquivos e prompts para um webhook HTTP do n8n e retorne uma resposta estruturada de forma que eu possa usá-la em fluxos de IA sem acoplamento.

**Why this priority**: Habilita recursos avançados de processamento de linguagem natural (como OCR e IA em PDFs) nas automações de forma flexível e reusável.

**Independent Test**: Invocar o método `enviar_para_ia` passando um arquivo simulado e um webhook local ou simulado, validando o recebimento da requisição HTTP POST e o retorno do dicionário JSON.

**Acceptance Scenarios**:

1. **Given** um arquivo local e uma mensagem de prompt, **When** a função de integração com n8n for executada com um webhook válido, **Then** o sistema deve ler o arquivo de forma genérica e despachar uma requisição multipart POST HTTP.
2. **Given** uma resposta bem-sucedida do servidor do n8n, **When** o cliente n8n a processa, **Then** ele deve converter a carga útil em um dicionário Python estruturado e retorná-lo para a automação chamadora.

### Edge Cases

- **Banco de Dados Corrompido ou Ausente**: Se o banco `automacao.db` não puder ser lido ou estiver corrompido, o sistema deve inicializar uma nova estrutura vazia baseada em tabelas padrão e exibir um aviso não obstrutivo na UI para o usuário, ao invés de quebrar a inicialização do app.
- **Falha Crítica na Thread de Automação**: Se um procedimento levantar uma exceção não tratada na sua thread de execução, o sistema orquestrador deve interceptar a falha, registrar o traceback completo nos logs, atualizar o status do procedimento na interface gráfica para "Falhou" e liberar a interface de modo seguro.
- **Webhook n8n Indisponível ou Lento**: Se a requisição ao webhook do n8n falhar devido a queda de conexão ou timeout de rede, a função do cliente n8n deve lançar uma exceção de rede clara e o procedimento chamador deve capturá-la para tentar novamente ou reportar o erro ao usuário de forma amigável.
- **Campos de Configuração Dinâmica Faltantes na UI**: Se um procedimento declarar configurações inválidas ou vazias em `fixed_settings` ou `variable_settings`, a interface gráfica deve gerar campos genéricos padrão ou exibir uma mensagem de erro indicando configuração inválida para aquele procedimento ao invés de falhar na renderização.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST manter um banco de dados local SQLite contido no arquivo `automacao.db`.
- **FR-002**: O sistema MUST implementar a busca e listagem de processos utilizando paginação no banco de dados com cláusulas `LIMIT` e `OFFSET` no arquivo `core/database.py`.
- **FR-003**: O método `obter_processos_paginados` MUST aceitar paginação, filtro de status de processos e uma string de busca por texto livre.
- **FR-004**: O cliente do n8n (`core/n8n_client.py`) MUST exportar uma função genérica `enviar_para_ia(webhook_url, arquivo_path, prompt)`.
- **FR-005**: O cliente do n8n MUST enviar os dados por requisição HTTP POST (multipart/form-data) e converter a resposta final do webhook em um dicionário Python (JSON estruturado).
- **FR-006**: O cliente do n8n MUST ser livre de lógica de negócios específica do projeto.
- **FR-007**: O sistema MUST expor a classe abstrata de base `BaseProcedure` em `core/base_procedure.py` para todos os procedimentos.
- **FR-008**: A classe `BaseProcedure` MUST exigir a implementação das propriedades abstratas `fixed_settings`, `variable_settings` e do método `run(settings, log_callback)`.
- **FR-009**: O carregador de procedimentos MUST varrer dinamicamente a pasta `procedures/` em busca de arquivos contendo subclasses de `BaseProcedure` registradas em seu `__init__.py`.
- **FR-010**: A interface gráfica (`ui/app.py`) MUST ser desenvolvida utilizando a biblioteca CustomTkinter.
- **FR-011**: O código da interface gráfica MUST ser desacoplado do backend, proibindo importação direta de conexões do SQLite, requisições HTTP diretas ao n8n ou processamento interno de PDFs no arquivo da UI.
- **FR-012**: A interface gráfica MUST incluir botões de paginação e campos de busca com atraso de debounce ou botão explícito de pesquisa para a tabela de processos.
- **FR-013**: A execução de qualquer procedimento via UI MUST rodar em threads assíncronas separadas utilizando `threading.Thread` para prevenir o bloqueio da interface de usuário.
- **FR-014**: O sistema MUST atualizar um componente de console de logs na interface de usuário usando um mecanismo de callback que mantenha no máximo as últimas N linhas de log visíveis.

### Key Entities *(include if feature involves data)*

- **Processo**: Representa um processo cadastrado no banco de dados local. Possui atributos como número do processo, tipo, status, histórico de execuções e data do último processamento.
- **Procedimento**: Objeto modular que implementa uma lógica de automação específica (ex: exportador, indexador). Define suas próprias propriedades e parâmetros de interface dinâmica.
- **Configuração de Automação**: Estrutura contendo parâmetros estáticos de rede/caminho (`fixed_settings`) e parâmetros dinâmicos de execução (`variable_settings`) associados a cada procedimento.
- **Registro de Log**: Mensagem de texto emitida pela automação indicando o progresso atual do processamento, acompanhada de carimbo de data/hora e nível de severidade.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O carregamento e exibição de dados de uma página da tabela local na interface gráfica CustomTkinter não deve exceder 500 milissegundos para um volume de até 10.000 processos no banco.
- **SC-002**: A interface gráfica desktop deve permanecer 100% responsiva (permitindo cliques e redimensionamentos) durante a execução de automações de longa duração via thread secundária.
- **SC-003**: Um novo desenvolvedor adicionando um procedimento compatível em `procedures/` e incluindo-o no `__init__.py` deve ter suas configurações fixas e variáveis automaticamente renderizadas na UI ao reiniciar o sistema, sem qualquer alteração no código da UI.
- **SC-004**: O console de logs da interface de usuário deve renderizar as atualizações enviadas via callback com latência inferior a 100 milissegundos.

## Assumptions

- O banco de dados SQLite `automacao.db` existirá ou será criado automaticamente pelo backend na inicialização do sistema desktop.
- As dependências externas de rede do webhook n8n estarão operacionais sob as URLs configuradas nos arquivos `.env`.
- O processamento de arquivos PDF e as execuções de Playwright serão contidos estritamente nos procedimentos (plugins) específicos, mantendo o núcleo da arquitetura genérico e livre de bibliotecas pesadas se o usuário não ativá-las.
- O sistema é voltado para uso em ambiente desktop local (Windows) onde o CustomTkinter e dependências locais de Python (como SQLite) estão instalados e configurados.
