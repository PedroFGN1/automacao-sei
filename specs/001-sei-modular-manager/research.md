# Technical Research: Gerenciador de Automações SEI Modular

**Feature**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/001-sei-modular-manager/spec.md)

## Decision Logs

### 1. Mecanismo de Carregamento Dinâmico de Procedimentos (Plugins)

- **Decision**: Utilizar carregamento dinâmico automático com a biblioteca nativa `importlib` do Python, combinado com o módulo `inspect` para descobrir classes filhas de `BaseProcedure` dentro do pacote `procedures`.
- **Rationale**: Permite que qualquer script adicionado à pasta `procedures/` que implemente a interface abstrata seja carregado e exposto na interface do usuário na inicialização do app, reduzindo o atrito para desenvolvedores e mantendo o core do projeto intacto.
- **Alternatives considered**:
  - *Registro manual estático* em arquivo de configuração: Rejeitado porque exige alteração de múltiplos arquivos e aumenta a chance de erros humanos.
  - *Bibliotecas de plugins de terceiros (ex: stevedore)*: Rejeitado para evitar sobrecarregar as dependências de instalação em ambientes desktop restritos de produção.

---

### 2. Persistência e Paginação de Processos no SQLite

- **Decision**: Uso da biblioteca nativa `sqlite3` com comandos SQL diretos parametrizados utilizando cláusulas `LIMIT` e `OFFSET`.
- **Rationale**: O SQLite é embarcado, super rápido e não requer um servidor de banco de dados rodando na máquina do usuário. A paginação em nível de banco de dados impede o carregamento excessivo de memória na máquina do cliente, garantindo que o tempo de resposta da UI seja menor que 500ms mesmo com mais de 10.000 processos cadastrados.
- **Alternatives considered**:
  - *SQLAlchemy ORM*: Rejeitado para o escopo inicial para evitar dependências extras, mas o design modular permite que o arquivo `core/database.py` mude para SQLAlchemy no futuro sem que a UI note a diferença.
  - *Banco de dados JSON local (como TinyDB)*: Rejeitado porque não escala eficientemente para grandes volumes de dados e carece de buscas otimizadas com indexação.

---

### 3. Execução Assíncrona de Automações e Atualização de Logs na UI

- **Decision**: Executar o método `run` do procedimento em uma thread de trabalho dedicada via `threading.Thread` e passar um callback que envia mensagens de logs. A UI lerá esses logs e atualizará a tela.
- **Rationale**: O loop de eventos de interfaces Tkinter (CustomTkinter) é síncrono e roda na thread principal. Qualquer processamento longo (como Playwright raspando dados do SEI ou OCR de PDFs) trava a UI se executado nela. O uso de threads separa a execução da automação e o callback atualiza a caixa de texto de log de forma fluida.
- **Alternatives considered**:
  - *asyncio (Programação Assíncrona)*: Rejeitado porque a integração entre o loop de eventos assíncrono do Python (`asyncio`) e o loop de eventos do Tkinter é instável e propensa a travar a interface.
  - *Multiprocessing (Múltiplos Processos)*: Rejeitado devido à complexidade de comunicação entre processos e ao consumo extra de memória RAM, sendo o isolamento por thread suficiente e mais leve.

---

### 4. Cliente Genérico n8n

- **Decision**: Requisições HTTP POST multipart estruturadas usando a biblioteca `requests` para enviar dados binários (PDFs) e prompts.
- **Rationale**: Fornece um cliente agnóstico de regras de negócio que simplifica o consumo do webhook do n8n, retornando um dicionário legível com o resultado obtido.
- **Alternatives considered**:
  - *urllib.request nativa*: Rejeitada porque a montagem de requisições multipart/form-data na biblioteca nativa do Python é verbosa e propensa a erros, enquanto `requests` lida com isso de forma nativa e limpa.
