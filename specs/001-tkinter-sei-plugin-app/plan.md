# Implementation Plan: Interface Desktop com Plugins para Automação do SEI

**Branch**: `001-tkinter-sei-plugin-app` | **Date**: 2026-07-15 | **Spec**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/001-tkinter-sei-plugin-app/spec.md)

**Input**: Feature specification from `/specs/001-tkinter-sei-plugin-app/spec.md`

## Summary

O objetivo é transformar os scripts de automação isolados do SEI em uma aplicação desktop integrada usando a biblioteca Tkinter, adotando uma arquitetura modular baseada em plugins. O sistema principal carregará dinamicamente novas automações de uma pasta de plugins, gerando a interface visual e os campos de parâmetros em tempo de execução. Para garantir a segurança operacional dos fluxos de trabalho existentes, os scripts legados da raiz (`enviar_n8n.py`, `exportador_sei.py`, `indexador_pdf.py` e seus arquivos `.bat`) serão totalmente mantidos intactos, e a lógica correspondente será portada para novos módulos de plugin dentro de `src/plugins/`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Playwright (1.61.0), PyPDF (6.14.2) e biblioteca padrão Tkinter (nativa do Python)

**Storage**: Planilhas locais em formato Excel/CSV para salvar os resultados dinâmicos das automações e banco SQLite local `automacao.db` para as operações legadas portadas.

**Testing**: pytest para validar o carregamento de plugins e a lógica dos robôs isoladamente.

**Target Platform**: Windows Desktop (compatível com os arquivos de lote `.bat` atuais).

**Project Type**: desktop-app (aplicação Tkinter executada localmente).

**Performance Goals**: Inicialização da UI principal em menos de 2 segundos; tempo de carregamento dinâmico de todos os plugins na inicialização inferior a 500ms.

**Constraints**:
- O thread de interface do Tkinter nunca deve congelar (uso obrigatório de `threading` secundária).
- Instâncias do Chrome depuradas remotamente (CDP) ou navegadores Playwright iniciados devem ser fechados de forma limpa, prevenindo processos órfãos na memória.

**Scale/Scope**: Execução de 1 automação concorrente de cada vez. Suporte a carregamento ilimitado de plugins dinâmicos que herdem de `BasePlugin` e estejam na pasta de plugins.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

O projeto não possui regras de governança ou constraints restritivas no arquivo de constituição atual. O design proposto atende aos critérios gerais de modularidade extrema, facilidade de manutenção e baixo acoplamento.

## Project Structure

### Documentation (this feature)

```text
specs/001-tkinter-sei-plugin-app/
├── plan.md              # Este arquivo (plano de implementação)
├── research.md          # Pesquisa de concorrência Tkinter e carregamento dinâmico
├── data-model.md        # Entidades e ciclo de vida de execução de robôs
├── quickstart.md        # Instruções de instalação e testes
├── contracts/
│   └── plugin-contract.md # Especificação do contrato para criação de novos plugins
└── checklists/
    └── requirements.md  # Checklist de qualidade da especificação
```

### Source Code Layout

Conforme decisão técnica e instruções do usuário, os arquivos de script e lotes legados são preservados na raiz, e a nova estrutura modular é criada sob a pasta `src/`.

```text
# Arquivos legados mantidos intactos na raiz
├── enviar_n8n.py
├── exportador_sei.py
├── indexador_pdf.py
├── iniciar_chrome_debug.bat
├── iniciar_exportador_isolado.bat
├── iniciar_indexador.bat
├── processos.txt
├── requirements.txt
...

# Nova estrutura da aplicação desktop modular
src/
├── app.py                # Arquivo principal que inicia o mainloop do Tkinter
├── core/
│   ├── __init__.py
│   ├── plugin_base.py    # Interface abstrata BasePlugin
│   ├── plugin_manager.py # Varredura de diretório e carregador de módulos
│   └── executor.py       # Gerenciador de threads e envio de logs por fila de mensagens
└── plugins/
    ├── __init__.py
    ├── enviar_n8n_plugin.py     # Cópia adaptada da automação do n8n para plugin
    ├── exportador_sei_plugin.py # Cópia adaptada do exportador do SEI para plugin
    └── indexador_pdf_plugin.py  # Cópia adaptada do indexador de PDFs para plugin

tests/
├── __init__.py
├── test_plugin_manager.py       # Testes unitários para carga dinâmica de plugins
└── test_plugins_contracts.py     # Testes de conformidade de contrato das automações portadas
```

**Structure Decision**: A pasta `src/` isola a aplicação desktop com plugins, enquanto a raiz do projeto preserva os scripts legados. Essa decisão atende perfeitamente ao requisito de manter execuções individuais via `.bat` funcionando de forma intocada no repositório.
