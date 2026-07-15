# Quickstart: Gerenciador de Automações SEI Modular

**Feature**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/001-sei-modular-manager/spec.md)

Este guia orienta o setup inicial, execução e extensão do sistema de automação modular.

## 1. Instalação e Configuração

Certifique-se de utilizar um ambiente virtual Python (ex: `.venv`) na versão 3.11 ou superior.

### Instalar Dependências

No terminal do projeto, execute:
```bash
pip install -r requirements.txt
```

### Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env` na raiz do projeto com as seguintes chaves de configuração:
```env
# URL do webhook de IA do n8n
N8N_WEBHOOK_URL=https://n8n.seu-dominio.com/webhook/identificador-ia
```

## 2. Executando a Aplicação Desktop

Para iniciar a interface gráfica do gerenciador:
```bash
python main.py
```
O banco de dados SQLite local `automacao.db` será inicializado automaticamente na primeira execução com a estrutura de tabelas necessária.

## 3. Desenvolvendo uma Nova Automação (Plugin)

Para estender o sistema com um novo procedimento de automação:

1. **Crie o arquivo do script** na pasta `procedures/` (ex: `procedures/indexador_sei.py`).
2. **Implemente a classe** herdando de `BaseProcedure` importada de `core.base_procedure`.
3. **Declare as configurações** necessárias retornando dicionários nas propriedades `fixed_settings` e `variable_settings`.
4. **Escreva o código de automação** no método `run(self, settings, log_callback)`.
5. **Registre o procedimento** no arquivo `procedures/__init__.py` adicionando a classe à exportação do módulo (ex: `__all__ = ["ExportadorSei", "IndexadorSei"]`).

## 4. Executando Testes de Validação

Para certificar-se de que as camadas estão funcionando perfeitamente sem erros de regressão, execute a suíte de testes usando pytest:
```bash
pytest
```
Os testes cobrirão a paginação do banco de dados, o cliente genérico do n8n e o contrato de carregamento de procedimentos.
