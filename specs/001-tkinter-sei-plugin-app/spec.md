# Feature Specification: Interface Desktop com Plugins para Automação do SEI

**Feature Branch**: `001-tkinter-sei-plugin-app`

**Created**: 2026-07-15

**Status**: Draft

**Input**: User description: "Quero tranformar esse ambiente de automações isoladas em arquivos em uma aplicação desktop com tkinter, o objetivo é ter uma aplicação com flexibilidade e configuração dinâmica de forma que quando desenvolver um nova automação seja fácil encaixá-la no backend e frontend. A automação será focada no site do SEI e no ciclo de vida dos processos dentro dele, por exemplo, quero poder desenvolver um bot que navague no sei e identifique quais processos são novos e já recolha o número deles e também já adicione prazo a eles. Dessa forma, o foco será automação no sei (navegação, recolher informações, procedimentos), a automação pode ter fontes de dados que não estejam no banco (exemplo: planilha com número de processos, caminho de arquivos a serem lidos, pdfs, etc...) então é bom deixar a flexibilidade de leitura de dados para ser passado ao bot. Por fim, ressalto a necessidade da arquitetura modular e nenhum bot ligado diretamente a outro, o comportamente deve ser de plugin."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execução de uma Automação do SEI via Interface (Priority: P1)

Como operador das automações, quero abrir a aplicação desktop, visualizar as automações disponíveis, selecionar a automação de interesse (ex: indexar processos ou exportar dados do SEI), preencher os parâmetros necessários exigidos por ela (ex: caminhos de arquivos, credenciais, configurações) e iniciá-la para que o trabalho seja executado automaticamente.

**Why this priority**: Esta é a jornada core que substitui os scripts isolados (.bat/.py) por uma interface gráfica unificada, entregando valor imediato ao operador.

**Independent Test**: Pode ser testado abrindo o aplicativo, selecionando um robô de teste na lista, preenchendo as entradas requeridas por ele e verificando se ele executa e exibe o status de sucesso/falha na UI.

**Acceptance Scenarios**:

1. **Given** que o aplicativo foi iniciado e exibe a lista de robôs/plugins disponíveis, **When** o usuário seleciona um robô, **Then** a interface atualiza dinamicamente para mostrar os campos de entrada (parâmetros) específicos exigidos por aquele robô.
2. **Given** que o usuário preencheu corretamente os parâmetros obrigatórios e clicou em "Iniciar", **When** o robô estiver executando, **Then** o botão de execução fica desabilitado para evitar cliques repetidos e a interface exibe o status de execução atualizado.
3. **Given** que o robô finaliza seu processamento, **When** a execução for concluída com sucesso ou erro, **Then** a interface apresenta visualmente o resultado (sucesso, aviso ou erro detalhado) e reabilita o controle de início.

---

### User Story 2 - Adição Simplificada de Nova Automação / Mecanismo de Plugins (Priority: P2)

Como desenvolvedor de automações, quero criar um novo arquivo python em um diretório específico de plugins e definir suas configurações e lógica sem precisar modificar o código principal da interface gráfica (Tkinter), para que o novo robô seja disponibilizado automaticamente no menu e formulário do sistema.

**Why this priority**: Garante a extensibilidade e escalabilidade do projeto à medida que novos procedimentos no SEI forem automatizados, sem acoplamento e sem risco de quebrar automações existentes.

**Independent Test**: Pode ser testado criando um arquivo dummy de plugin na pasta de plugins do sistema. Ao reiniciar a interface gráfica, o novo plugin dummy deve aparecer na lista e seu formulário de parâmetros dinâmicos deve ser renderizado corretamente na UI.

**Acceptance Scenarios**:

1. **Given** que um novo arquivo de plugin é colocado no diretório correto seguindo a interface ou contrato estabelecido, **When** a aplicação desktop for carregada, **Then** a lista de automações do menu exibe o novo robô com seu nome amigável.
2. **Given** que o novo plugin define em seu contrato que precisa de parâmetros específicos (ex: uma pasta de PDFs e uma senha), **When** o usuário seleciona esse robô na UI, **Then** os campos correspondentes (um selecionador de diretório e um campo de texto de senha oculto) são desenhados dinamicamente na tela.

---

### User Story 3 - Passagem Flexível de Fontes de Dados Externas (Priority: P3)

Como operador de robôs complexos, quero fornecer arquivos de entrada específicos (ex: planilhas .xlsx/.csv, arquivos text ou pastas de PDFs) no formulário do robô para alimentar a automação com dados que não estão armazenados no banco de dados local.

**Why this priority**: Permite que automações ad-hoc operem com planilhas de trabalho diário enviadas por outros departamentos ou lotes específicos de arquivos PDFs locais.

**Independent Test**: Pode ser testado selecionando um robô que exige um arquivo Excel como entrada, carregando a planilha pelo explorador de arquivos na UI, e verificando se a automação recebe e consome esses dados corretamente.

**Acceptance Scenarios**:

1. **Given** que um robô requer um arquivo externo como fonte de dados, **When** o usuário clica no seletor de arquivos na UI, **Then** o sistema abre a caixa de diálogo nativa de seleção de arquivo limitando as extensões permitidas configuradas pelo plugin.

---

### Edge Cases

- **Plugin Malformado**: O que acontece se um arquivo de plugin contiver erros de sintaxe ou violar a interface esperada? O sistema principal de carregamento de plugins deve tratar a exceção isoladamente, registrar o erro em logs e permitir que a aplicação inicialize exibindo as demais automações válidas, sem quebrar o sistema.
- **Fechamento Inesperado**: O que acontece se o usuário fechar a janela da aplicação enquanto um robô estiver executando tarefas no navegador SEI? A aplicação deve interceptar o evento de fechamento, emitir um aviso e encerrar com segurança os processos e sessões abertas do robô para evitar processos zumbis do navegador em background.
- **Falha de Conectividade ou Timeout no SEI**: Como o sistema lida se o SEI estiver fora do ar ou se a página demorar para carregar além do limite máximo configurado? O bot deve abortar a execução, liberar os recursos de navegação e reportar na interface o status detalhado da falha de timeout.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema de interface desktop deve ser desenvolvido usando a biblioteca padrão Tkinter.
- **FR-002**: O sistema principal deve escanear dinamicamente um diretório dedicado a plugins (ex: `/plugins`) ao inicializar para registrar os robôs disponíveis.
- **FR-003**: Cada plugin de automação deve ser auto-contido e expor metadados estruturados (nome, descrição, parâmetros necessários) e um método de execução unificado.
- **FR-004**: O sistema de UI deve desenhar dinamicamente os inputs baseando-se nos metadados de parâmetros expostos pelo plugin ativo selecionado.
- **FR-005**: O sistema deve permitir que plugins de automação operem de forma independente do banco de dados, aceitando arquivos locais e dados do usuário diretamente.
- **FR-006**: A execução de uma automação deve ser feita em uma thread separada. O andamento da execução deve ser exibido em tempo real através de uma área de logs (campo de texto rolável) integrada na interface gráfica, e qualquer erro fatal ocorrido deve abrir uma caixa de diálogo (pop-up) nativa alertando o usuário.
- **FR-007**: O comportamento de navegação no SEI deve ser configurável por meio de uma opção visual (Checkbox) na interface gráfica, permitindo que o usuário escolha se deseja rodar em segundo plano (Headless) ou com o navegador visível (padrão ativo: modo visível).
- **FR-008**: O armazenamento dos dados resultantes de cada execução (como lista de processos processados, prazos, etc.) deve ser exportado e gravado localmente na forma de planilhas de dados (arquivos CSV ou Excel), facilitando o compartilhamento e visualização pelo operador.

### Key Entities *(include if feature involves data)*

- **Plugin**: Representa o módulo independente de automação. Possui metadados (nome, descrição, especificação dos parâmetros de entrada) e o ponto de entrada da execução (run).
- **Parâmetro de Entrada (InputParameter)**: Define as especificações de cada dado exigido pelo robô (ex: tipo de dado como 'texto', 'arquivo', 'diretório', 'booleano', se é obrigatório, e label amigável).
- **Sessão do Robô (RobotSession)**: Gerencia o ciclo de vida da execução de um robô específico, incluindo o estado de execução (pendente, rodando, sucesso, erro), tempo de duração e logs gerados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo necessário para um desenvolvedor registrar uma nova automação básica na interface gráfica e executá-la com parâmetros de texto não deve passar de 15 minutos (sem necessidade de reescrever lógica na UI).
- **SC-002**: 100% dos plugins com erros de sintaxe ou violações de contrato do sistema são isolados na inicialização, gerando avisos específicos no log, sem impedir a abertura do aplicativo principal.
- **SC-003**: 100% das execuções que falham por timeouts de rede no SEI devem encerrar as instâncias do navegador de apoio em até 30 segundos, liberando memória.

## Assumptions

- A aplicação desktop rodará em ambiente Windows (compatível com a infraestrutura atual baseada em arquivos `.bat`).
- Os plugins utilizarão ferramentas de automação web padrão do ecossistema Python (Selenium, Playwright, ou similar, já instalados no `.venv`).
- Cada automação é responsável por gerenciar internamente o parsing de suas fontes de dados fornecidas (ex: ler arquivos xlsx com pandas, processar PDFs com PyPDF, etc.).
- A autenticação no SEI será fornecida como um dos parâmetros dinâmicos obrigatórios para os robôs que necessitarem de login, não havendo um sistema global e centralizado de cofre de senhas na primeira versão.
- As dependências de bibliotecas de terceiros dos plugins serão instaladas no ambiente virtual (`.venv`) principal da aplicação.
