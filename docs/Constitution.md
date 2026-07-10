# Projeto Automação SEI: Diretrizes e Constituição de Arquitetura

Este documento serve como a **Constituição Arquitetural** para o projeto de automação do SEI. Ele foi projetado como um manual técnico e conceitual de referência para que qualquer Inteligência Artificial (ou engenheiro de software) possa compreender a fundo as decisões de design, a estrutura de dados e as particularidades do DOM do SEI 5.0.4.

---

## 🎯 1. Propósito e Escopo

O objetivo do projeto é realizar o download automatizado em lote de arquivos PDF completos de processos do **SEI (Sistema Eletrônico de Informações)**.
A automação é projetada para rodar em ambientes locais do Windows, suportando grandes volumes de dados (lotes de 3.000+ processos) de forma resiliente, permitindo pausas, retornos e fornecendo logs de auditoria detalhados.

---

## 🏗️ 2. Arquitetura do Sistema e Fluxo de Dados

A automação baseia-se em quatro pilares fundamentais: **Fila Persistente**, **Verificação Física de Integridade**, **Automação Web Resiliente** e **Auditoria pós-execução**.

```
  [ processos.txt ] (Entrada)
         │
         ▼
 ┌───────────────┐
 │ Deduplicação  │ (Python: dict.fromkeys)
 └───────┬───────┘
         │
         ▼
 ┌───────────────┐       Sincroniza      ┌─────────────────────────────────┐
 │   SQLite DB   │ ────────────────────> │ Tabela processos                │
 │ (automacao.db)│                       │ - status: PENDENTE/SUCESSO/FALHA│
 └───────┬───────┘                       └─────────────────────────────────┘
         │
         ▼
 ┌─────────────────────────────────┐
 │ Varredura Física (Auto-Skip)    │ ──> Se PDF existe e tem > 1KB:
 └───────┬─────────────────────────┘     Marca SUCESSO no banco e pula.
         │
         ▼ (Apenas Pendentes)
 ┌─────────────────────────────────┐
 │ Loop Executor (Playwright)      │ <── Política de Re-tentativa (1 retry)
 └───────┬─────────────────────────┘
         │
         ▼
 ┌───────────────┐
 │ Relatório TXT │ (Saída)
 └───────────────┘
```

---

## 💾 3. Persistência de Estado (SQLite Schema)

O controle transacional da fila de execução é feito localmente no arquivo `automacao.db` através da tabela `processos`.

### Esquema SQL (DDL)
```sql
CREATE TABLE IF NOT EXISTS processos (
    numero_processo TEXT PRIMARY KEY,
    status TEXT NOT NULL,              -- Valores: 'PENDENTE', 'SUCESSO', 'FALHA'
    tentativas INTEGER DEFAULT 0,      -- Contador de execuções (limite de 2 por corrida)
    ultima_execucao TEXT,              -- Timestamp formatado (YYYY-MM-DD HH:MM:SS)
    mensagem_erro TEXT                 -- Stack trace ou string do erro em caso de FALHA
);
```

### Regras de Manipulação de Estado:
1. **Deduplicação Inicial**: Toda lista de entrada lida de `processos.txt` é limpa de linhas duplicadas via Python preservando a ordem usando `list(dict.fromkeys(processos))`.
2. **Sincronização (`INSERT OR IGNORE`)**: Ao iniciar o script, novos registros são inseridos como `PENDENTE`. Registros antigos de corridas passadas são ignorados, preservando seus status históricos (`SUCESSO` ou `FALHA`).
3. **Filtro de Execução**: O lote de execução é filtrado dinamicamente para processar apenas processos cujo `status` no banco de dados seja diferente de `SUCESSO` e que estejam descritos na lista atual de `processos.txt`.
4. **Resiliência de Escrita**: Cada processo atualiza o banco de dados imediatamente ao finalizar (sucesso ou falha), garantindo que, se o script for interrompido, nenhum progresso seja perdido.

---

## 🌐 4. Mapeamento do DOM e Estratégia de Frames (SEI 5.0.4)

O SEI 5.0.4 utiliza uma arquitetura baseada em iframes aninhados que exige locators encadeados precisos. O mapeamento físico e as sequências de clique são descritos abaixo.

### Hierarquia de Frames no Painel Direito:
```
Página Principal (Raiz)
  └── iframe com ID/Name "#ifrConteudoVisualizacao" (Painel da Direita - Menu de Ações)
        └── iframe com ID/Name "#ifrVisualizacao" (Nested Frame - Conteúdo dos Documentos)
```

### Protocolo de Interação Web (Passo a Passo):
1. **Busca Rápida**: Inserir o número do processo no elemento `#txtPesquisaRapida` presente na página raiz (ou varrer frames de 1º nível) e pressionar `Enter`.
2. **Carga do Painel**: Aguardar o elemento `#ifrConteudoVisualizacao` ficar visível na página raiz.
3. **Pausa para Renderização**: Aplicar um `time.sleep(2.5)` para garantir a carga do iframe interno `#ifrVisualizacao` e carregamento das classes do SEI.
4. **Botão de PDF (Acesso)**: O link para a página de geração reside no frame `#ifrConteudoVisualizacao` (Pai).
   - *Selector principal*: `a[href*='acao=procedimento_gerar_pdf']` ou `img[src*='processo_gerar_pdf']`.
   - *Locator*: `page.frame_locator("#ifrConteudoVisualizacao").locator(selector)`.
5. **Navegação de Geração**: O clique no botão abre a tela de geração do PDF. Devido ao atributo `target="ifrVisualizacao"`, o formulário de PDF é renderizado no iframe filho `#ifrVisualizacao`.
6. **Seleção de Opções**:
   - *Foco*: `frame = page.frame_locator("#ifrConteudoVisualizacao").frame_locator("#ifrVisualizacao")`.
   - *Radio Button ("Todos")*: Marcar o elemento `input[value='T']` ou `input[name='rdoTipo'][value='T']`.
   - *Botão Gerar (Submissão)*: Localizar e clicar no elemento `button[name='btnGerar']`.
7. **Interceptação de Download**: Utilizar `page.expect_download()` (do objeto `Page` e **nunca** de `BrowserContext`) englobando o clique no botão `Gerar` para capturar a stream do arquivo e salvá-lo como `C:\SEI_Exportacoes\<numero_processo>.pdf`.

---

## 📈 5. Monitoramento de Progresso e Métricas

O script não utiliza dependências de terceiros (como `tqdm` ou `rich`) para desenhar barras de progresso, mantendo-se leve e autossuficiente.

- **Fórmula do ETA**: O tempo restante (ETA) é calculado dividindo o tempo total decorrido pelo número de processos **efetivamente processados** (excluindo os que foram pulados instantaneamente pelo Auto-Skip), multiplicando o tempo médio resultante pelo número de processos pendentes na fila.
- **Relatório pós-lote**: Ao término de cada execução, um log formatado é salvo na pasta de exportações como `relatorio_execucao_YYYY-MM-DD_HH-MM-SS.txt` listando estatísticas globais e detalhamento descritivo de todas as falhas registradas na corrida para fins de depuração.

---

## 📜 6. Regras de Ouro para Alteração do Código

Qualquer modificação futura conduzida por IA deve seguir rigidamente estas regras:
1. **Sincronia de Scripts**: Quaisquer alterações na lógica do SEI (seletores, delays, fluxos) devem ser implementadas de forma idêntica tanto em `exportador_sei.py` (CDP/Chrome Debug) quanto em `exportador_sei_isoleted.py` (Navegador Isolado/Persistente).
2. **Sem Variáveis de Contexto Globais**: O `page` e o `context` do Playwright devem ser passados como parâmetros explícitos das funções auxiliares, evitando acoplamento global.
3. **Deduplicação de Fila**: Nunca remova a higienização de chaves duplicadas para evitar travamentos de escrita no banco de dados SQLite.
4. **Fechamento de Conexões**: Toda conexão SQLite aberta nas funções auxiliares deve ser explicitamente encerrada (`conn.close()`) para evitar locks de gravação de arquivos de banco.
