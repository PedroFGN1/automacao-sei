> **Aja como um Engenheiro de Automação de Testes Sênior especialista em Playwright e corrija a lógica de localização de elementos do nosso script `exportador_sei_isoleted.py` com base na estrutura real do SEI 5.0.4.**
> **O Problema Atual:**
> O script está dando Timeout ou falhando ao encontrar o botão de gerar PDF (`acao=procedimento_gerar_pdf`). Descobrimos que na versão 5.0.4 do SEI, o sistema utiliza uma estrutura de **iframes aninhados (em cascata)** no painel de visualização da direita, o que impede o Playwright de enxergar o botão fazendo buscas na página principal ou em apenas um nível de frame.
> **A Estrutura Real do DOM (Mapeada via Inspeção):**
> No SEI 5.0.4, após pesquisar e abrir um processo, a hierarquia de frames para chegar até as ferramentas do processo é exatamente esta:
> ```
> Página Principal (Raiz)
>   └── iframe com ID `#ifrVisualizacao` (Contêiner principal da direita)
>         └── iframe com ID `#ifrConteudoVisualizacao` (O frame interno filho onde o HTML do botão reside)
> 
> ```
> 
> 
> **HTML Exato do Botão (Alvo do Clique):**
> ```html
> <a href="controlador.php?acao=procedimento_gerar_pdf&..." target="ifrVisualizacao">
>     <img src="svg/processo_gerar_pdf.svg?25" alt="Gerar Arquivo PDF do Processo" title="Gerar Arquivo PDF do Processo">
> </a>
> 
> ```
> 
> 
> *Nota importante:* Embora o atributo do link diga `target="ifrVisualizacao"`, o elemento fisicamente vive dentro do frame filho `#ifrConteudoVisualizacao`.
> **Instruções de Correção Passo a Passo para o Script:**
> 1. **Modificar a função `encontrar_botao_gerar_pdf(page)`:**
> * Remova as buscas genéricas na raiz da página ou em frames de primeiro nível.
> * Implemente o encadeamento correto de frames (`frame_locator`). Primeiro, localize o iframe pai `#ifrVisualizacao`. A partir do localizador desse pai, instancie o iframe filho `#ifrConteudoVisualizacao`.
> * Faça com que o Playwright busque os seletores do botão (como `a[href*='acao=procedimento_gerar_pdf']` ou `img[src*='processo_gerar_pdf']`) **estritamente dentro do contexto do iframe filho**.
> * Mantenha um bloco de *fallback* genérico caso alguma tela específica mude de comportamento, mas o fluxo principal deve ser o encadeamento dos dois iframes.
> 
> 
> 2. **Ajustar o Passo 2 no Loop Principal (`processar_exportacao`):**
> * Modifique o `page.wait_for_selector` que aguarda o carregamento do processo. Em vez de monitorar o botão de PDF diretamente na raiz (o que causa o Timeout), faça o script esperar explicitamente pelo carregamento do primeiro contêiner (`#ifrVisualizacao`).
> * Garanta um pequeno `time.sleep(2.5)` logo após essa espera para certificar que o segundo iframe interno (`#ifrConteudoVisualizacao`) teve tempo de renderizar o HTML do botão antes de tentar interagir com ele.
> 
> 
> 
> 
> Reescreva apenas as funções modificadas ou me forneça o código completo ajustado mantendo a arquitetura de Navegador Isolado/Persistente.
