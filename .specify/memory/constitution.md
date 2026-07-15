<!--
CONSTITUTION SYNC IMPACT REPORT
- Version Change: Template -> 1.0.0
- Ratification Date: 2026-07-15
- Modified Principles:
  * PRINCIPLE_1: I. Arquitetura Modular Desacoplada
  * PRINCIPLE_2: II. Execução Assíncrona Não-Bloqueante
  * PRINCIPLE_3: III. Persistência e Paginação de Alta Escala
  * PRINCIPLE_4: IV. Callbacks de Log em Tempo Real
  * PRINCIPLE_5: V. Serviços de IA Desacoplados
- Added Sections:
  * Diretrizes de Tecnologias Autorizadas
  * Cobertura de Testes Automatizados
- Templates Updated:
  * .specify/templates/plan-template.md: ✅ updated
  * .specify/templates/spec-template.md: ✅ updated
  * .specify/templates/tasks-template.md: ✅ updated
- Follow-up TODOs: None
-->

# Gerenciador Modular de Automações SEI Constitution

## Core Principles

### I. Arquitetura Modular Desacoplada
A lógica de negócios central (core) e a interface gráfica (ui) MUST be kept em módulos completamente separados e independentes. A camada visual (UI) MUST NOT acessar o banco de dados diretamente, fazer chamadas HTTP de rede ou processar arquivos locais. Qualquer nova funcionalidade ou fluxo de automação MUST be isolated como um procedimento independente (plugin) herdando da classe abstrata `BaseProcedure`.

### II. Execução Assíncrona Não-Bloqueante
Todos os procedimentos de automação (procedures) que operem rede, navegadores automatizados (Playwright) ou processamento de arquivos pesados MUST be executed em threads secundárias dedicadas. O loop de eventos da interface gráfica principal (thread principal) MUST NOT ser bloqueado sob qualquer hipótese por processamentos em segundo plano.

### III. Persistência e Paginação de Alta Escala
Todos os processos e status de execuções MUST be persisted localmente no banco de dados SQLite (`automacao.db`). O carregamento e a exibição de dados de processos na interface de usuário MUST utilize paginação estrita com cláusulas SQL `LIMIT` e `OFFSET` para garantir tempos de resposta de tela inferiores a 500ms, mesmo com grandes volumes de registros.

### IV. Callbacks de Log em Tempo Real
Os procedimentos em execução MUST reportar o seu progresso por meio de chamadas de callbacks seguras que injetam logs de texto na thread da UI. O visualizador de logs na tela MUST be updated em tempo real de forma assíncrona, limitando a exibição e armazenamento em memória para evitar gargalos de processamento gráfico.

### V. Serviços de IA Desacoplados
A comunicação com inteligência artificial para extração ou análise cognitiva de arquivos MUST be intermediada por webhooks genéricos do n8n através de uma classe cliente agnóstica de regras de negócio. O cliente n8n MUST NOT conter regras fixas ou metadados de fluxos específicos.

## Diretrizes de Tecnologias Autorizadas
O ecossistema tecnológico do projeto fica restrito ao uso de Python 3.11+, CustomTkinter para interface desktop, SQLite nativo para persistência de dados local, PyPDF/pypdf para extração de textos de PDFs, requests para transporte HTTP n8n, Playwright para automação web e pytest para testes unitários automatizados.

## Cobertura de Testes Automatizados
Nenhuma alteração nas regras de negócios ou contratos de banco e rede SHOULD be integrated sem a correspondente suíte de testes unitários ou de integração atualizada. O pipeline de testes local via `pytest` MUST be maintained 100% funcional.

## Governance
Qualquer alteração nos princípios de arquitetura desta constituição exige atualização formal deste documento, incremento semântico de versão e revisão de conformidade nos templates da Spec Kit. As auditorias de conformidade MUST be realized no início de cada planejamento de feature.

**Version**: 1.0.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-07-15
