# Directory Model: Reorganização Física do Repositório

Este documento descreve o modelo físico de transição dos diretórios e arquivos do repositório, mapeando a origem e destino de cada recurso.

## 1. Mapeamento de Movimentação de Arquivos

A tabela a seguir define as ações de movimentação física que serão realizadas no repositório. Nenhuma lógica interna de processamento será modificada, apenas referências de caminhos e pacotes.

| Arquivo/Pasta Origem | Ação | Arquivo/Pasta Destino | Descrição |
| :--- | :--- | :--- | :--- |
| `src/` | **Renomear / Mover** | `app/` | Código-fonte do aplicativo desktop Tkinter e plugins. |
| `tests/` | **Mover** | `app/tests/` | Testes unitários do aplicativo modular de plugins. |
| `exportador_sei.py` | **Mover** | `scripts/exportador_sei.py` | Script legado de execução direta do exportador. |
| `exportador_sei_isoleted.py` | **Mover** | `scripts/exportador_sei_isoleted.py` | Script legado do exportador isolado com perfil. |
| `exportador_sei_isoleted_debug.py` | **Mover** | `scripts/exportador_sei_isoleted_debug.py` | Script legado de depuração do exportador. |
| `indexador_pdf.py` | **Mover** | `scripts/indexador_pdf.py` | Script legado do indexador de PDFs e busca rápida. |
| `enviar_n8n.py` | **Mover** | `scripts/enviar_n8n.py` | Script legado de envio de PDFs para o webhook n8n. |
| `iniciar_chrome_debug.bat` | **Mover** | `bin/iniciar_chrome_debug.bat` | Lote para iniciar Chrome debug na porta 9222. |
| `iniciar_exportador_isolado.bat` | **Mover** | `bin/iniciar_exportador_isolado.bat` | Lote para rodar o exportador isolado legado. |
| `iniciar_exportador_isolado_debug.bat` | **Mover** | `bin/iniciar_exportador_isolado_debug.bat` | Lote para depuração do exportador isolado. |
| `iniciar_indexador.bat` | **Mover** | `bin/iniciar_indexador.bat` | Lote para rodar o indexador de PDFs legado. |

## 2. Padrões de Exclusão de Movimentação

Os arquivos a seguir **permanecem intactos na raiz** do projeto para manter a configuração global de ambiente estável:
- `.gitignore`
- `.env`
- `requirements.txt`
- `url_sei.txt`
- `processos.txt` (usado como entrada default)
- `.venv/` (ambiente virtual Python)
- `.specify/` e subpastas de controle do Spec Kit
- `specs/` (pasta contendo as especificações e planos das features)
- `AGENTS.md` (contexto de agentes)
