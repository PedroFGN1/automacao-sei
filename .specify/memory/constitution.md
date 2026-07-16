<!--
Sync Impact Report:
- Version change: None -> 1.0.0 (Ratificação inicial da constituição)
- List of modified principles:
  * [PRINCIPLE_1_NAME] -> I. Arquitetura Modular de Plugins
  * [PRINCIPLE_2_NAME] -> II. Preservação de Legado e Retrocompatibilidade
  * [PRINCIPLE_3_NAME] -> III. Concorrência e Isolamento em Threads
  * [PRINCIPLE_4_NAME] -> IV. Resiliência e Tolerância a Falhas de Carregamento
  * [PRINCIPLE_5_NAME] -> V. Desempenho e Gerenciamento de Recursos Web
- Added sections:
  * Tecnologia e Dependências Regulamentadas
  * Workflow de Validação e Testes
- Removed sections: Nenhuma
- Templates requiring updates:
  * README.md (✅ atualizado)
  * docs/quickstart.md (⚠ pendente - quickstart.md da feature atualizado em specs/)
- Follow-up TODOs: Nenhum
-->

# SEI Automation Hub Constitution

## Core Principles

### I. Arquitetura Modular de Plugins
Toda automação de robô deve ser implementada como um plugin autônomo, herdando da interface BasePlugin e localizada no diretório src/plugins/. É estritamente proibido acoplamento direto ou importação de dependências mútuas entre plugins. Toda comunicação deve ocorrer exclusivamente via interfaces e contratos estabelecidos.

### II. Preservação de Legado e Retrocompatibilidade
Os scripts legados originais na raiz do projeto (enviar_n8n.py, exportador_sei.py, indexador_pdf.py e arquivos .bat correspondentes) devem permanecer totalmente intocados e operacionais para execuções individuais via console/terminal. Toda a nova interface e execução de plugin gráfica deve operar de maneira isolada na pasta src/.

### III. Concorrência e Isolamento em Threads
Para evitar o travamento da interface visual (congelamento do loop principal do Tkinter), toda execução de robô de automação (Playwright ou PyPDF) deve rodar de maneira assíncrona em uma thread dedicada (PluginExecutor). É mandatório o uso de filas de mensagens thread-safe (queue.Queue) para a passagem de logs em tempo real para a UI.

### IV. Resiliência e Tolerância a Falhas de Carregamento
Erros de importação, sintaxe ou de execução interna em um plugin não podem indisponibilizar a inicialização do sistema principal. O gerenciador de plugins (PluginManager) deve isolar falhas de importação de arquivos malformados de forma graciosa, registrando avisos nos logs sem interromper a execução dos plugins válidos.

### V. Desempenho e Gerenciamento de Recursos Web
Toda automação baseada em Playwright conectada via protocolo CDP (Chrome DevTools Protocol) deve gerenciar e encerrar adequadamente as conexões de rede e abas do navegador utilizadas ao final de sua execução ou caso ocorra um fechamento inesperado do aplicativo desktop, prevenindo processos órfãos do Chrome na memória.

## Tecnologia e Dependências Regulamentadas

O ecossistema do aplicativo desktop de automação fica regulamentado sob o uso de:
- **Interface Gráfica**: Biblioteca nativa Tkinter com estilos ttk.
- **Automação Web**: Playwright com conexões CDP na porta 9222.
- **Extração de Texto**: pypdf para arquivos PDF.
- **Persistência local**: Banco de dados SQLite local (automacao.db) e planilhas estruturadas (Excel/CSV).

## Workflow de Validação e Testes

Todo novo plugin de automação desenvolvido deve passar pela validação do contrato de interface BasePlugin e garantia de inicialização através do conjunto de testes automatizados unitários em tests/test_plugin_manager.py. A execução bem-sucedida do unittest local em ambiente virtual (.venv) é pré-requisito obrigatório antes do commit e merge de código.

## Governance

- A alteração de qualquer princípio core ou restrição técnica nesta constituição requer atualização documental detalhada e o incremento da versão semântica do documento.
- Todo pull request deve passar pelo crivo de conformidade com as regras desta constituição.

**Version**: 1.0.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-07-16
