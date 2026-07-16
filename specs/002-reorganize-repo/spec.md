# Feature Specification: Reorganização Física do Repositório

**Feature Branch**: `002-reorganize-repo`

**Created**: 2026-07-16

**Status**: Draft

**Input**: User description: "Quero reorganizar o repositório, no momento tem o projeto de app na pasta src e script soltos com os .bat, não quero alterar nenhuma lógica de código nessa spec, só quero que o que do aplicativo fique dentro de uma pasta app e o que é de scripts individuais fique em uma outra pasta, e os excutáveis fique em outra. Meu objetivo é facilitar o desenvolvimento de novas lógicas de código de automação, então quando eu quiser criar um novo script para testar um lógica quero garantir que não vou impactar o aplicativo e também que eu possa executar aquela lógica isolada caso eu queira por um .bat, além disso quando eu validar um novo script de automação quero poder passar para a IA a intrução dela ler essa automação e incluir no app então ter essa visão separada em pastas iria separar qual script pode ser executado isolado e qual tem que ser junto ao aplicativo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execução Integrada do Aplicativo na Nova Pasta (Priority: P1) 🎯 MVP

Como desenvolvedor ou operador do sistema, quero executar o aplicativo de automação gráfico a partir do seu novo diretório estruturado, para que a interface Tkinter e seus plugins carreguem e executem perfeitamente.

**Why this priority**: Esta é a principal entrega, pois garante que a migração física do código-fonte da aplicação não introduza erros de importação e que o aplicativo continue operacional.

**Independent Test**: Executar o aplicativo gráfico no novo diretório com o interpretador python e confirmar se os plugins em `app/plugins/` são carregados sem falhas na UI e se os testes automatizados da aplicação continuam passando.

**Acceptance Scenarios**:

1. **Given** que a pasta `src/` foi renomeada para a pasta da aplicação, **When** eu executo a aplicação, **Then** todos os módulos internos do núcleo (`core/`) e da pasta de plugins são importados com sucesso.
2. **Given** que o aplicativo foi iniciado, **When** eu executo a verificação de testes unitários do carregador de plugins, **Then** todos os testes passam com sucesso apontando para os novos diretórios.

---

### User Story 2 - Execução Isolada de Scripts de Automação Individuais (Priority: P2)

Como desenvolvedor de automações, quero colocar meus novos arquivos de script individuais para testes ad-hoc em uma pasta separada, de forma que eu possa codificar lógicas experimentais sem qualquer risco de interferência na pasta principal da aplicação ou nos seus plugins.

**Why this priority**: Garante o isolamento exigido para criar novos fluxos antes de decidir incorporá-los ao aplicativo principal.

**Independent Test**: Criar um arquivo python de teste na pasta de scripts individuais e executá-lo individualmente, validando que ele roda de forma autônoma.

**Acceptance Scenarios**:

1. **Given** que os scripts individuais foram movidos para a sua nova pasta, **When** um novo script de teste é adicionado a esta pasta, **Then** ele não é detectado ou carregado pelo gerenciador de plugins da aplicação ao iniciar o aplicativo gráfico.

---

### User Story 3 - Execução de Automações por Arquivos de Lote (.bat) (Priority: P3)

Como operador de automações, quero dar um duplo clique nos arquivos de lote `.bat` em sua nova pasta dedicada para disparar as execuções individuais correspondentes (como abrir o Chrome em depuração ou rodar o indexador) de forma direta e sem erros de caminho de arquivos.

**Why this priority**: Mantém as automações individuais legadas facilmente executáveis e funcionais em lote no Windows pelo operador.

**Independent Test**: Clicar em um arquivo `.bat` na pasta dedicada e certificar-se de que ele inicia o processo correto (ex: inicia o Chrome com depuração ativa ou dispara a execução de um script individual na pasta de scripts).

**Acceptance Scenarios**:

1. **Given** que os executáveis `.bat` foram movidos para sua nova pasta de destino, **When** eu clico no lote de iniciar o Chrome com debug, **Then** ele executa o comando invocando o navegador corretamente.
2. **Given** que eu clico no lote de iniciar uma automação legada, **When** o processo inicia, **Then** ele executa o script individual correspondente localizado na sua nova pasta com sucesso.

---

### Edge Cases

- **Paths nos Executáveis (.bat)**: O que acontece com as referências relativas a arquivos de scripts e banco de dados dentro dos arquivos `.bat` após mudarem de pasta? Todos os caminhos nos scripts `.bat` devem ser ajustados para refletir a nova estrutura física relativa das pastas.
- **Imports entre módulos**: O que acontece com os `import` relativos ou absolutos de subdiretórios locais na aplicação ao mover a pasta principal `src/`? Os imports devem ser inspecionados e ajustados caso a alteração do nome da raiz da aplicação de `src` para `app` interfira nas chamadas.
- **Banco de dados local (automacao.db)**: Como os caminhos de leitura e escrita do banco de dados SQLite são tratados pelos scripts individuais e de aplicação? O local do arquivo do banco de dados deve ser de fácil parametrização para não quebrar com a movimentação.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema principal de código-fonte da aplicação desktop Tkinter (atualmente em `src/`) deve ser integralmente movido para o novo diretório 'app/', e a pasta de testes unitários ('tests/') deve ser posicionada dentro de 'app/tests/'.
- **FR-002**: Os scripts legados de execução individual (`enviar_n8n.py`, `exportador_sei.py`, `indexador_pdf.py` etc.) devem ser movidos para uma pasta dedicada a scripts de desenvolvimento e testes.
- **FR-003**: Os arquivos de lote do Windows (`.bat`) devem ser movidos para uma pasta dedicada de executáveis.
- **FR-004**: Todas as referências de caminhos de arquivos relativos internos e chamadas de importação de submódulos nos scripts e arquivos `.bat` devem ser atualizadas para manter o funcionamento original inalterado.
- **FR-005**: A lógica dos arquivos de código, seletores DOM e comportamento dos robôs não deve sofrer alterações de escopo ou de funcionalidade.
- **FR-006**: Os arquivos de lote do Windows `.bat` devem ser atualizados para usar caminhos dinâmicos relativos com a variável '%~dp0' do Windows (ex: '%~dp0..\scripts\nome_script.py'), garantindo portabilidade em qualquer repositório local.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos testes unitários da aplicação de carregamento de plugins passam com sucesso executando a partir da nova pasta de código da aplicação.
- **SC-002**: 100% das execuções de arquivos `.bat` a partir da nova pasta executam os scripts Python correspondentes com sucesso, sem erros de "arquivo não encontrado".
- **SC-003**: Nenhum arquivo da aplicação desktop de plugins (como `app.py` ou os arquivos de `plugins/`) é misturado ou afetado pela adição de novos scripts de teste na pasta de automações isoladas.

## Assumptions

- A reorganização manterá a compatibilidade com o ambiente virtual `.venv` existente na raiz do projeto.
- O banco de dados `automacao.db` continuará a ser operado pelos robôs, devendo suas novas referências de caminhos ser atualizadas se necessário.
- A estrutura de especificações em `specs/` continuará na raiz do repositório.
