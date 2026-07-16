# Implementation Plan: Reorganização Física do Repositório

**Branch**: `002-reorganize-repo` | **Date**: 2026-07-16 | **Spec**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/002-reorganize-repo/spec.md)

**Input**: Feature specification from `/specs/002-reorganize-repo/spec.md`

## Summary

O objetivo é reestruturar fisicamente o repositório organizando seus arquivos em diretórios dedicados (`app/`, `scripts/` e `bin/`) para separar o aplicativo desktop Tkinter das automações individuais legadas e seus atalhos `.bat`. Conforme restrição explícita do usuário, **nenhuma lógica de processamento de código deve ser alterada**. As modificações no código-fonte limitam-se estritamente à atualização dos caminhos de importação do Python (renomeando o pacote `src` para `app`) e ajuste das referências relativas a arquivos e interpretador nos scripts de lote `.bat` do Windows.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Playwright (1.61.0), PyPDF (6.14.2), requests, Tkinter

**Storage**: Arquivo de banco SQLite local `automacao.db` e planilhas locals.

**Testing**: unittest (para testes unitários da aplicação)

**Target Platform**: Windows Desktop (para execução de arquivos `.bat` e Tkinter).

**Project Type**: desktop-app & scripts

**Performance/Quality Goals**: Garantir que as automações e testes continuem executando exatamente com as mesmas velocidades e comportamentos de antes da migração, com zero quebra de caminhos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Este plano está em total conformidade com a Constituição v1.0.0 ratificada para o projeto:
- **Princípio I (Modularidade)**: Preservado. Os plugins do app continuam isolados sob `app/plugins/`.
- **Princípio II (Preservação de Legado)**: Preservado e otimizado. Os scripts legados continuam operando de forma isolada do app, agora sob a pasta `scripts/`, com seus atalhos `.bat` reunidos em `bin/`.

## Project Structure

A transição física do layout de arquivos do repositório é definida a seguir:

### Estrutura Físíca Antiga (Atual)
```text
├── src/
│   ├── app.py
│   ├── core/
│   └── plugins/
├── tests/
│   └── test_plugin_manager.py
├── enviar_n8n.py
├── exportador_sei.py
├── exportador_sei_isoleted.py
├── exportador_sei_isoleted_debug.py
├── indexador_pdf.py
├── iniciar_chrome_debug.bat
├── iniciar_exportador_isolado.bat
├── iniciar_exportador_isolado_debug.bat
├── iniciar_indexador.bat
├── processos.txt
├── requirements.txt
...
```

### Estrutura Física Nova (Alvo)
```text
├── app/                  # Nova pasta da aplicação desktop (antiga src/)
│   ├── app.py
│   ├── core/
│   ├── plugins/
│   └── tests/            # Pasta de testes movida para dentro de app/
│       └── test_plugin_manager.py
├── scripts/              # Nova pasta dos scripts individuais/legados
│   ├── enviar_n8n.py
│   ├── exportador_sei.py
│   ├── exportador_sei_isoleted.py
│   ├── exportador_sei_isoleted_debug.py
│   └── indexador_pdf.py
├── bin/                  # Nova pasta dos executáveis/atalhos .bat
│   ├── iniciar_chrome_debug.bat
│   ├── iniciar_exportador_isolado.bat
│   ├── iniciar_exportador_isolado_debug.bat
│   └── iniciar_indexador.bat
├── processos.txt         # Mantido na raiz
├── requirements.txt      # Mantido na raiz
├── .env                  # Mantido na raiz
├── url_sei.txt           # Mantido na raiz
└── .venv/                # Mantido na raiz
```

**Structure Decision**: A reorganização utiliza as pastas `app/`, `scripts/` e `bin/` para separar as preocupações. A lógica do aplicativo gráfico é isolada em `app/` e os scripts manuais em `scripts/`. Os arquivos `.bat` atualizados com `%~dp0` residem em `bin/`.
