# Implementation Plan: Gerenciador de Automações SEI Modular

**Branch**: `001-sei-modular-manager` | **Date**: 2026-07-15 | **Spec**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/001-sei-modular-manager/spec.md)

**Input**: Feature specification from `/specs/001-sei-modular-manager/spec.md`

## Summary

O objetivo é implementar o Gerenciador de Automações SEI Modular, um sistema desktop leve em Python com arquitetura estritamente desacoplada (Backend core vs. Frontend ui). A interface gráfica é construída em CustomTkinter e renderiza dinamicamente as configurações de procedimentos de automação independentes (carregados dinamicamente da pasta `procedures/`). A persistência de processos é feita localmente em um banco SQLite (`automacao.db`) com paginação eficiente e a execução dos procedimentos ocorre em threads separadas com comunicação de logs em tempo real por callbacks. Há também um cliente genérico integrado para IA via webhooks do n8n.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: CustomTkinter, requests, playwright (dentro de procedimentos de automação), pytest

**Storage**: SQLite (banco de dados local `automacao.db`)

**Testing**: pytest

**Target Platform**: Windows Desktop

**Project Type**: desktop-app / modular-automation

**Performance Goals**: Tempo de carregamento/atualização da tabela de processos < 500ms; atualização de console de logs na UI com latência < 100ms.

**Constraints**: Acoplamento zero do banco e rede na UI; execuções de procedimentos obrigadas a rodar em threads separadas (`threading.Thread`).

**Scale/Scope**: Suporte a múltiplos procedimentos estendidos; visualização otimizada para até 10.000+ processos locais.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípios do Projeto**: A constituição atual possui placeholders. Não foram encontradas violações de diretrizes de governança ou complexidades injustificadas.
- **Estrutura Modular**: A divisão estrita entre lógica (`core/`) e interface (`ui/`) respeita plenamente os padrões de baixo acoplamento e alta coesão recomendados.

## Project Structure

### Documentation (this feature)

```text
specs/001-sei-modular-manager/
├── plan.md              # Este arquivo (plano de implementação)
├── research.md          # Resultados de pesquisa (Phase 0)
├── data-model.md        # Modelo de dados local (Phase 1)
├── quickstart.md        # Guia de início rápido da feature (Phase 1)
└── checklists/
    └── requirements.md  # Checklist de qualidade da especificação
```

### Source Code (repository root)

```text
core/
├── __init__.py
├── database.py               # Persistência com paginação (SQLite)
├── n8n_client.py             # Cliente genérico para IA do n8n
├── pdf_processor.py          # Extrator de textos de PDFs
└── base_procedure.py         # Classe abstrata para automações (plugins)

procedures/
├── __init__.py               # Ponto de registro e carregamento dinâmico
├── exportador_sei.py         # Procedimento de exemplo (exportador)
└── novo_procedimento.py      # Espaço reservado para novas automações

ui/
├── __init__.py
├── app.py                    # Janela principal CustomTkinter (controlador da UI)
└── components/
    ├── __init__.py
    ├── paginated_table.py    # Componente visual de tabela paginada com buscas
    └── log_viewer.py         # Componente console de logs em tempo real

main.py                       # Ponto de partida do app desktop (Orquestrador)
requirements.txt              # Bibliotecas necessárias
.env                          # URL do webhook do n8n e credenciais de teste
```

**Structure Decision**: A organização segue exatamente a estrutura modular separada entre lógica de negócios pura (`core`), automações independentes (`procedures`) e interface desacoplada (`ui`), de modo a permitir migrações futuras simples (ex: para frameworks web/eel) sem impactar o backend.

## Complexity Tracking

*Nenhuma violação ou justificativa de complexidade necessária para esta implementação.*
