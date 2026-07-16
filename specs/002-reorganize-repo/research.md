# Research & Decisions: Reorganização Física do Repositório

Este documento registra as pesquisas de compatibilidade de caminhos e as decisões estruturais necessárias para migrar fisicamente os diretórios do repositório, garantindo compatibilidade total e zero alteração de lógica de código.

## Decisão 1: Mapeamento de Pastas do Repositório

### Contexto
Atualmente, o repositório possui uma pasta `src/` contendo o código da aplicação Tkinter e seus plugins, uma pasta `tests/` na raiz, e diversos scripts Python individuais e arquivos `.bat` dispersos na raiz. Precisamos separá-los logicamente.

### Escolha
Reorganizar a estrutura nos seguintes três diretórios na raiz do projeto:
1. `app/`: Contendo todo o código do aplicativo desktop Tkinter (`app.py`, subpastas `core/`, `plugins/` e `tests/` interna).
2. `scripts/`: Contendo os scripts Python individuais/legados (`enviar_n8n.py`, `exportador_sei.py`, `indexador_pdf.py` etc.) que operavam de forma isolada na raiz.
3. `bin/`: Contendo os arquivos de execução em lote do Windows (`.bat`).

### Rationale
- Mantém o aplicativo Tkinter totalmente autocontido em `app/` (incluindo seus testes unitários em `app/tests/`).
- Isola scripts ad-hoc e testes de novas ideias em `scripts/`, impedindo que afetem o carregamento de plugins da aplicação gráfica.
- Centraliza executáveis rápidos em `bin/`, limpando o diretório raiz do repositório.

---

## Decisão 2: Atualização de Imports de Módulos (Python)

### Contexto
Vários arquivos da aplicação utilizam imports absolutos que começam com o prefixo `src.`. Exemplo em `tests/test_plugin_manager.py` ou nos plugins:
`from src.core.plugin_base import BasePlugin`
Ao renomear `src/` para `app/`, essas chamadas dispararão erros de `ModuleNotFoundError`.

### Escolha
Atualizar sistematicamente todos os pacotes e arquivos de importação dentro de `app/` para utilizarem o prefixo `app.` no lugar de `src.`.

### Rationale
- O interpretador Python interpretará a nova pasta `app/` como o pacote raiz do aplicativo.
- O `app/core/plugin_manager.py` será configurado para varrer a pasta `app/plugins/` (adicionando este caminho ao `sys.path` dinamicamente se necessário).

---

## Decisão 3: Portabilidade e Caminhos Dinâmicos nos arquivos `.bat`

### Contexto
Ao mover os arquivos `.bat` para a pasta `bin/` e os scripts que eles executam para a pasta `scripts/`, os comandos originais que assumiam a execução na raiz do repositório falharão.

### Escolha
Utilizar a variável especial do interpretador de comandos CMD do Windows `%~dp0`.

### Rationale
- A variável `%~dp0` expande para o caminho completo do diretório onde o próprio arquivo `.bat` está localizado (incluindo a barra invertida final).
- Usando `%~dp0..\`, podemos subir um nível do diretório para referenciar o ambiente virtual `.venv` na raiz e os scripts na pasta `scripts/`.
- Exemplo de adaptação do script `iniciar_exportador_isolado.bat`:
  ```batch
  @echo off
  %~dp0..\.venv\Scripts\python.exe %~dp0..\scripts\exportador_sei_isoleted.py
  pause
  ```
- Isso garante que a execução funcione via duplo clique no Explorer ou invocação via linha de comando a partir de qualquer diretório ativo.
