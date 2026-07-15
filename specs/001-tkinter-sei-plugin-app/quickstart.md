# Quickstart: Interface Desktop com Plugins para Automação do SEI

Este guia descreve como configurar, executar e estender a nova aplicação desktop modular Tkinter de automações do SEI.

## 1. Instalação e Configuração

### Pré-requisitos
A aplicação desktop foi projetada para rodar em ambiente Windows utilizando a mesma infraestrutura atual do projeto.
- Python 3.11+
- Virtual Environment (`.venv`) ativado e atualizado.

### Passos de Inicialização
1. Certifique-se de que o ambiente virtual está ativo:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
2. Instale/verifique as dependências necessárias listadas no `requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```
3. Inicialize o Chrome em modo de depuração remota (necessário se for executar robôs que se conectam a uma sessão ativa do SEI):
   ```powershell
   iniciar_chrome_debug.bat
   ```
4. Execute a aplicação desktop principal:
   ```powershell
   python src/app.py
   ```

---

## 2. Como Criar e Acoplar uma Nova Automação (Plugin)

Para criar um novo bot sem tocar no código-fonte principal da interface gráfica, siga estes passos:

1. **Crie o Arquivo do Plugin**: Na pasta `src/plugins/`, crie um novo arquivo python (ex: `limpador_sei_plugin.py`).
2. **Implemente a Classe**: Escreva uma classe herdando de `BasePlugin` (importada de `src.core.plugin_base`):
   ```python
   from src.core.plugin_base import BasePlugin
   
   class LimpadorSeiPlugin(BasePlugin):
       @property
       def id(self) -> str:
           return "limpador_sei"
           
       @property
       def name(self) -> str:
           return "Limpador de Processos do SEI"
           
       @property
       def description(self) -> str:
           return "Automação para arquivar processos antigos do SEI."
           
       def get_params_schema(self):
           return [
               {"name": "limite_dias", "type": "text", "label": "Dias Inativos", "default": "30", "is_required": True}
           ]
           
       def execute(self, params, logger):
           limite = int(params["limite_dias"])
           logger("Iniciando varredura de processos...", "INFO")
           # ... Lógica do robô ...
           logger("Processo concluído com sucesso!", "INFO")
           return {"status": "sucesso", "arquivados": 15}
   ```
3. **Inicialize a Interface**: O `PluginManager` detectará o novo arquivo e o exibirá no menu da aplicação.

---

## 3. Preservação dos Scripts Legados

Os scripts legados contidos na raiz do projeto (`enviar_n8n.py`, `exportador_sei.py`, `indexador_pdf.py` e seus arquivos `.bat` auxiliares) **não foram alterados**.
Você pode continuar executando-os individualmente pelo prompt de comando ou agendador de tarefas do Windows exatamente da mesma forma como fazia antes da implementação do aplicativo gráfico.
A lógica da aplicação modular em `src/` utiliza cópias adaptadas desses robôs para garantir total isolamento de código.

---

## 4. Como Rodar os Testes Unitários

Para garantir que o carregador de plugins e as implementações de contrato estão funcionando perfeitamente, utilize o `pytest`:
```powershell
pytest tests/
```
