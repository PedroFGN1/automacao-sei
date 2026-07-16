# Quickstart: Workspace Reorganizado

Este guia descreve como rodar e testar os componentes do projeto após a reorganização física das pastas do repositório.

## 1. Executando o Aplicativo Desktop Principal

A aplicação desktop modular de plugins foi movida da antiga pasta `src/` para a pasta `app/`.

### Como iniciar
Execute o ponto de entrada principal `app.py` utilizando o interpretador do ambiente virtual da raiz:
```powershell
.\.venv\Scripts\python.exe app/app.py
```

---

## 2. Executando os Scripts Individuais (Legados)

Os scripts de automação isolados foram agrupados no diretório `scripts/` para liberar a raiz do projeto.

### Como iniciar manualmente
Para rodar qualquer um dos scripts individuais legados, invoque o python indicando a nova pasta:
```powershell
.\.venv\Scripts\python.exe scripts/exportador_sei.py
.\.venv\Scripts\python.exe scripts/indexador_pdf.py
.\.venv\Scripts\python.exe scripts/enviar_n8n.py
```

---

## 3. Utilizando os Arquivos de Lote (.bat)

Os atalhos executáveis em lote `.bat` foram centralizados na pasta `bin/`.

### Como iniciar
1. Abra a pasta `bin/` no Windows Explorer.
2. Dê um duplo clique no arquivo `.bat` desejado (ex: `iniciar_chrome_debug.bat` ou `iniciar_exportador_isolado.bat`).
3. O script utilizará caminhos relativos baseados no diretório do atalho e disparará a execução corretamente.

---

## 4. Executando os Testes Unitários

A suite de testes unitários foi migrada de `tests/` para `app/tests/`.

### Como rodar os testes
Execute o unittest nativo do Python apontando para a nova pasta de testes:
```powershell
.\.venv\Scripts\python.exe -m unittest app/tests/test_plugin_manager.py
```
Todos os testes de carga de plugins devem passar sem avisos ou erros.
