# SPEC PARA O AGENTE DE IA: GERENCIADOR DE AUTOMAÇÕES SEI MODULAR

> **Instruções para o Agente de IA:**
> Atue como um Engenheiro de Software Sênior especializado em Python, Arquitetura de Software e Automação de Processos. Seu objetivo é construir a estrutura de um sistema Desktop leve, com separação estrita de responsabilidades (Backend vs. Frontend) para permitir futuras migrações de interface (como para o framework Eel).
> 
> 

---

## 🏛️ ARQUITETURA GERAL DO PROJETO

A estrutura de pastas deve seguir rigorosamente a separação de conceitos:

```text
automacao-sei/
│
├── core/                         # Backend Puro (Lógica de Negócios)
│   ├── __init__.py
│   ├── database.py               # Persistência (SQLite/SQLAlchemy) com paginação
│   ├── n8n_client.py             # Cliente genérico e isolado do n8n
│   ├── pdf_processor.py          # Manipulação e extração de dados de PDFs
│   └── base_procedure.py         # Classe abstrata/base para procedimentos
│
├── procedures/                   # Scripts de Automação Independentes (Plugins)
│   ├── __init__.py
│   ├── exportador_sei.py         # Procedimento 1 (Exemplo)
│   └── novo_procedimento.py      # Procedimento 2 (Exemplo)
│
├── ui/                           # Frontend Desacoplado (Interface Gráfica)
│   ├── __init__.py
│   ├── app.py                    # Janela Principal (CustomTkinter)
│   └── components/               # Componentes visuais (Tabela paginada, Logs)
│
├── main.py                       # Ponto de entrada do sistema (Orquestrador)
├── requirements.txt              # Dependências do projeto
└── .env                          # Variáveis de ambiente

```

---

## 🛠️ REQUISITOS TÉCNICOS E ESPECIFICAÇÃO DOS COMPONENTES

### 1. Camada de Persistência (`core/database.py`)

* **Função:** Gerenciar a conexão com o banco SQLite (`automacao.db`).


* **Requisito de Performance:** Implementar métodos de busca que utilizem paginação SQL (`LIMIT` e `OFFSET`).


* **Método Necessário:**
```python
def obter_processos_paginados(pagina: int, itens_por_pagina: int, filtro_status: str = None, busca: str = None) -> list:
    # Retorna apenas o bloco de dados solicitado para evitar gargalos na UI.
    pass

```



### 2. Integração Genérica do n8n (`core/n8n_client.py`)

* **Função:** Serviço agnóstico para envio de payloads ao n8n.


* **Design Modular:** Não deve conter nenhuma regra de negócio fixa. Deve expor uma função simples:
```python
def enviar_para_ia(webhook_url: str, arquivo_path: str, prompt: str) -> dict:
    # Lê o arquivo de forma genérica, envia junto com o prompt via POST HTTP para o n8n
    # e retorna um objeto (dicionário Python/JSON) com o resultado processado pela IA.
    pass

```



### 3. Arquitetura Modular de Procedimentos (`core/base_procedure.py`)

* **Função:** Definir o contrato (interface) que toda nova automação criada deve seguir.
* **Padrão de Configuração:** Deve expor como o procedimento se autodeclara (ajudando a UI a renderizar formulários dinâmicos).
* **Interface Abstrata:**
```python
from abc import ABC, abstractmethod

class BaseProcedure(ABC):
    @property
    @abstractmethod
    def fixed_settings(self) -> dict:
        """Configurações estáticas necessárias (ex: URLs, credenciais, caminhos de rede)"""
        pass

    @property
    @abstractmethod
    def variable_settings(self) -> dict:
        """Configurações variáveis de execução (ex: caminho de uma planilha excel, intervalo de datas)"""
        pass

    @abstractmethod
    def run(self, settings: dict, log_callback) -> bool:
        """Método principal de execução da automação (utilizando Playwright ou manipulando PDFs)"""
        pass

```



### 4. Criação de Novos Procedimentos (`procedures/`)

* Qualquer novo arquivo nesta pasta que herde de `BaseProcedure` e seja colocado no `__init__.py` deve ser detectado automaticamente pelo sistema, preenchendo dinamicamente as opções de automação na tela do usuário.

### 5. Frontend Isolado (`ui/`)

* **Tecnologia:** CustomTkinter.
* **Desacoplamento Estrito:** A camada de UI **não** pode fazer conexões com banco de dados diretamente, nem disparar requisições HTTP, nem manipular arquivos. Ela deve instanciar e chamar os métodos do `core/` ou de controladores intermediários.
* **UI/UX para Grandes Volumes de Dados:**
* **Tabela:** Implementar paginação com botões "Anterior" e "Próximo" e indicador de "Página X de Y".
* **Campos de Busca:** Campo de entrada de texto com atraso (debounce) ou botão de pesquisa para filtrar os processos por número ou tipo no banco local.


* **Execução Assíncrona:** Toda chamada de automação (`procedure.run()`) deve ser disparada em uma thread separada (`threading.Thread`) para garantir que a UI se mantenha fluida e responsiva.


* **Callback de Log:** Passar uma função de callback para o procedimento em execução. Essa função deve atualizar uma caixa de texto dinâmica na UI com os logs gerados em tempo real (exibindo apenas as últimas N linhas).





---

## 🚀 FLUXO DE DESENVOLVIMENTO SUGERIDO

Peça ao agente para codificar o projeto de forma iterativa, apresentando o código completo em etapas estruturadas:

1. **Etapa 1:** Estrutura do Banco de Dados com paginação no SQLite (`core/database.py`).


2. **Etapa 2:** Classe abstrata de Procedimentos (`core/base_procedure.py`) e o Cliente n8n (`core/n8n_client.py`).


3. **Etapa 3:** Um procedimento de exemplo (ex: `procedures/exportador_sei.py`) que implemente a classe base.


4. **Etapa 4:** A interface gráfica em CustomTkinter (`ui/app.py`), provando o isolamento do backend e a renderização dinâmica baseada em `fixed_settings` e `variable_settings`.
