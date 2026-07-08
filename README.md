# Automação de Exportação de PDFs do SEI

Este projeto automatiza o download em lote de arquivos PDF de processos do SEI (Sistema Eletrônico de Informações) utilizando a biblioteca **Playwright** em Python.

O script conecta-se a uma instância ativa do **Google Chrome** (que já deve estar logada no SEI) na porta de depuração remota `9222`. Ele simula os cliques reais do usuário para contornar o parâmetro dinâmico `infra_hash` das requisições e evitar bloqueios.

---

## 🛠️ Requisitos de Instalação e Preparação

### 1. Preparar o Ambiente Python
O script utiliza a biblioteca `playwright`. Nós já instalamos ela no seu ambiente virtual (`.venv`).

Caso precise rodar em outro local ou reconfigurar, execute:
```bash
.venv\Scripts\pip install playwright
```

### 2. Iniciar o Google Chrome no Modo de Depuração
Para que o Playwright consiga se conectar ao seu navegador logado, você precisa iniciar o Google Chrome na porta `9222`.

1. **Feche completamente** todas as janelas abertas do Google Chrome (certifique-se no Gerenciador de Tarefas de que não há processos remanescentes).
2. Abra o menu Iniciar do Windows, digite `Executar` (ou pressione `Win + R`).
3. Cole o seguinte comando e aperte **Enter**:
   ```cmd
   chrome.exe --remote-debugging-port=9222
   ```
4. O Google Chrome abrirá. **Acesse o seu SEI e faça login normalmente**. O script usará essa mesma aba para realizar as consultas e downloads.

---

## 🚀 Como Usar

1. **Definir a lista de processos**:
   Edite o arquivo [processos.txt](file:///C:/Users/pedro.galvao/Documents/automacao-sei/processos.txt) e adicione os números dos processos que deseja baixar, um por linha. Exemplo:
   ```text
   202600004061428
   202600004061543
   ```

2. **Executar o Script**:
   Com o Chrome aberto e logado na porta 9222, execute o script no terminal:
   ```powershell
   .venv\Scripts\python.exe exportador_sei.py
   ```

3. **Arquivos Gerados**:
   O script salvará todos os PDFs gerados na pasta **`C:\SEI_Exportacoes`**. Os arquivos serão nomeados de acordo com o número do processo (ex: `202600004061543.pdf`).

---

## 🛡️ Tratamento de Erros e Resiliência do Loop

O script [exportador_sei.py](file:///C:/Users/pedro.galvao/Documents/automacao-sei/exportador_sei.py) foi desenvolvido seguindo padrões de desenvolvimento sênior:
- **Resiliência do Loop**: Se um processo demorar para carregar ou não for encontrado, ele exibe a falha no console, aguarda o tempo de segurança e prossegue para o próximo processo.
- **Detecção Inteligente de Erros**: Identifica alertas nativos do SEI (processo inexistente ou sem permissão).
- **Seletores Multi-Versão**: Utiliza uma matriz de seletores comuns do SEI para encontrar a barra de pesquisa, o botão "Gerar PDF", o radio button e o botão de download, garantindo funcionamento em versões 3.x e 4.x do SEI.
- **Forçar Nó Raiz**: Caso o botão "Gerar PDF" não seja visível inicialmente, o script tenta clicar no nó do processo na árvore de documentos para abrir a capa e recarregar os botões.
