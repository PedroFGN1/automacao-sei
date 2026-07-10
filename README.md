# Automação de Exportação de PDFs do SEI

Este projeto fornece uma solução robusta e resiliente em **Python** e **Playwright** para realizar o download em lote de arquivos PDF completos de processos do **SEI (Sistema Eletrônico de Informações)**, especificamente otimizado para o **SEI 5.0.4**.

A automação é projetada para rodar de forma confiável em lotes massivos (mais de 3.000 processos), fornecendo rastreabilidade por banco de dados, barra de progresso no terminal e relatórios pós-execução.

---

## 🏗️ Estrutura do Repositório

- **[exportador_sei_isoleted.py](file:///C:/Users/pedro.galvao/Documents/automacao-sei/exportador_sei_isoleted.py)**: Script que gerencia e abre seu próprio navegador Chrome de forma isolada e persistente, armazenando a sessão de login localmente.
- **[exportador_sei.py](file:///C:/Users/pedro.galvao/Documents/automacao-sei/exportador_sei.py)**: Script alternativo que se conecta a uma instância do Chrome já aberta no seu computador (porta de depuração `9222`).
- **[processos.txt](file:///C:/Users/pedro.galvao/Documents/automacao-sei/processos.txt)**: Lista de entrada onde você insere os números dos processos a serem baixados (um por linha).
- **[automacao.db](file:///C:/Users/pedro.galvao/Documents/automacao-sei/automacao.db)**: Banco de dados SQLite criado automaticamente para armazenar e rastrear o estado da fila de exportação.
- **[docs/Constitution.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/docs/Constitution.md)**: Documento de constituição de arquitetura contendo especificações técnicas do DOM do SEI 5.0.4 para referência de IA/desenvolvedores.
- **[iniciar_exportador_isolado.bat](file:///C:/Users/pedro.galvao/Documents/automacao-sei/iniciar_exportador_isolado.bat)**: Script utilitário em lote para executar o extrator isolado com um duplo clique.
- **[iniciar_chrome_debug.bat](file:///C:/Users/pedro.galvao/Documents/automacao-sei/iniciar_chrome_debug.bat)**: Script em lote para abrir o Chrome na porta 9222 (para uso com o script alternativo).

---

## 🛠️ Requisitos de Instalação e Preparação

### 1. Ambiente Python
A biblioteca `playwright` deve estar instalada no seu ambiente virtual local (`.venv`).
Para garantir a instalação das dependências:
```bash
.venv\Scripts\pip install playwright
```

### 2. Definir a URL do SEI
Você pode definir a URL do SEI do seu órgão de duas formas:
- Editando a variável `SEI_URL` diretamente no topo dos scripts Python.
- Ou digitando a URL no terminal na primeira execução (o script criará automaticamente o arquivo `url_sei.txt` com o endereço para as próximas vezes).

---

## 🚀 Como Usar

### Opção A: Usando o Navegador Isolado (Recomendado)
Esta opção abre uma instância do Chrome totalmente limpa, mas mantém sua sessão salva em uma pasta local (`C:\SEI_Exportacoes\perfil_sei`), evitando que você precise fazer login a cada execução.

1. Insira os processos desejados no arquivo **[processos.txt](file:///C:/Users/pedro.galvao/Documents/automacao-sei/processos.txt)**.
2. Dê um duplo clique em **[iniciar_exportador_isolado.bat](file:///C:/Users/pedro.galvao/Documents/automacao-sei/iniciar_exportador_isolado.bat)** (ou execute `.venv\Scripts\python.exe exportador_sei_isoleted.py` no terminal).
3. Na janela do Chrome que se abrir, faça o login normalmente.
4. O script detectará o login e iniciará a exportação em lote automaticamente.

### Opção B: Usando a Porta de Depuração 9222
Ideal se você preferir rodar a automação diretamente no seu navegador Chrome principal de trabalho.

1. **Feche completamente** todas as janelas abertas do Google Chrome.
2. Dê um duplo clique em **[iniciar_chrome_debug.bat](file:///C:/Users/pedro.galvao/Documents/automacao-sei/iniciar_chrome_debug.bat)** para reabrir o Chrome em modo debug.
3. Acesse o SEI e faça o login na janela que se abriu.
4. No terminal, execute:
   ```bash
   .venv\Scripts\python.exe exportador_sei.py
   ```

---

## 📊 Recursos de Confiabilidade do Pipeline

- **Controle Transacional por SQLite**: Se o script for interrompido a qualquer momento, ao reiniciá-lo ele continuará exatamente do último processo pendente.
- **Auto-Skip**: PDFs já salvos na pasta **`C:\SEI_Exportacoes`** com tamanho maior que 1 KB são identificados e marcados como concluídos no banco de dados, evitando downloads repetidos.
- **Deduplicação Automática**: Linhas duplicadas no arquivo `processos.txt` são limpas automaticamente, mantendo a ordem correta e prevenindo erros de restrição de chave única no banco.
- **Política de Re-tentativa**: Falhas de carregamento ou download sofrem uma tentativa de re-execução imediata antes de marcar o processo como `FALHA` e pular para o próximo.
- **Interface e Relatório**: O terminal exibe uma barra de progresso em tempo real com estatísticas de sucesso/falha e cálculo de tempo restante (ETA). Ao término da corrida, um arquivo descritivo contendo os detalhes das falhas é gerado no diretório de exportação.
