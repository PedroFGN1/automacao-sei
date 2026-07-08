### Prompt de Correção para o Assistente de IA (Python/Playwright)

**Aja como um Engenheiro de Automação de Testes Sênior especialista em Playwright e revise o nosso script `exportador_sei.py` com base na estrutura real do SEI 5.0.4 mapeada abaixo.**
O script deve continuar se conectando à instância aberta do Chrome na porta `9222`, mas precisamos ajustar a estratégia de seletores e foco de frames para corresponder ao HTML exato do sistema.
**Mapeamento do HTML Real do Sistema:**
1. **Link do Processo na Tabela Geral:**
```html
<a class="processoNaoVisualizado" href="controlador.php?acao=procedimento_trabalhar...&id_procedimento=97623936..." ...>202600004061769</a>

```
  *Instrução:* A busca rápida deve nos levar para a página que contém o processo. Se o script usar uma lista de números, ele deve usar a barra de pesquisa rápida (`#txtPesquisaRapida`).
2. **Botão de Acesso às Opções de PDF (Menu Superior do Processo):**
 ```html
 <a href="controlador.php?acao=procedimento_gerar_pdf..." target="ifrVisualizacao"><img src="svg/processo_gerar_pdf.svg?25" alt="Gerar Arquivo PDF do Processo" title="Gerar Arquivo PDF do Processo"></a>
 
 ```
 
 
 *Instrução Importante:* Repare que o link está na página principal (raiz), mas tem o atributo `target="ifrVisualizacao"`. O script deve localizar esse elemento `a[href*="acao=procedimento_gerar_pdf"]` ou a imagem dentro dele **diretamente na página principal**, sem entrar em nenhum frame para clicar nele.
3. **Botão Final de Gerar PDF:**
 ```html
 <button tabindex="451" type="button" accesskey="G" name="btnGerar" value="Gerar" onclick="gerar();" class="infraButton"><span class="infraTeclaAtalho">G</span>erar</button>
 
 ```
 
 
 *Instrução Importante:* Após clicar no botão do passo anterior, as opções de PDF serão carregadas **dentro do iframe `#ifrVisualizacao**`. O script deve explicitamente dar um switch/foco para o frame `#ifrVisualizacao`, garantir a seleção do radio button de "Todos os documentos" (`input[value='T']`) e clicar neste elemento `button[name='btnGerar']`.
 
 
 **Refine as funções do script para garantir que:**
 * O clique no botão do PDF (`a[href*="acao=procedimento_gerar_pdf"]`) seja feito no contexto global da página (`page.locator`).
 * Após o clique, o script aguarde o carregamento do conteúdo dentro do iframe: `frame = page.frame_locator("#ifrVisualizacao")`.
 * Dentro desse frame, execute o clique em `button[name='btnGerar']` associado ao gerenciador de download do Playwright: `with context.expect_download(...)`.
 * Mantenha a resiliência do loop (try/except por processo) e o delay de 4 segundos entre processos.
 
 
 Forneça o código Python completo e corrigido.
