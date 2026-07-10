/**
 * SEI - Extrator em Lote de PDFs (Versão Corrigida e Aprimorada)
 * Melhores Práticas: Resolução de frames, URLs absolutas e interface visual de progresso.
 * 
 * Instruções:
 * 1. Acesse o SEI no seu navegador e vá para a tela de "Controle de Processos" (Caixa de Entrada).
 * 2. Abra o Console de Desenvolvedor (F12 ou Ctrl+Shift+I).
 * 3. Cole este script e aperte Enter.
 * 4. Certifique-se de permitir "Múltiplos Downloads" caso o navegador solicite.
 */

(async function() {
    // === CONFIGURAÇÕES ===
    const DELAY_MS = 4000; // Tempo de espera entre downloads para não sobrecarregar o servidor do SEI

    // === INTERFACE VISUAL (OVERLAY) ===
    const style = document.createElement('style');
    style.innerHTML = `
        #sei-extractor-panel {
            position: fixed; bottom: 20px; right: 20px; width: 380px;
            background: rgba(30, 30, 35, 0.85); backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px;
            color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 999999; padding: 16px;
            transition: all 0.3s ease; box-sizing: border-box;
        }
        #sei-extractor-title { font-weight: 600; font-size: 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        #sei-extractor-progress-bg { background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 12px; }
        #sei-extractor-progress-bar { background: linear-gradient(90deg, #3b82f6, #60a5fa); width: 0%; height: 100%; transition: width 0.4s ease; }
        #sei-extractor-status { font-size: 12px; color: #9ca3af; margin-bottom: 8px; }
        #sei-extractor-logs { background: rgba(0,0,0,0.3); border-radius: 6px; padding: 8px; height: 100px; overflow-y: auto; font-family: monospace; font-size: 11px; color: #a7f3d0; border: 1px solid rgba(255,255,255,0.05); }
        .log-entry { margin-bottom: 4px; }
        .log-error { color: #f87171; }
        .log-warn { color: #fbbf24; }
    `;
    document.head.appendChild(style);

    const panel = document.createElement('div');
    panel.id = 'sei-extractor-panel';
    panel.innerHTML = `
        <div id="sei-extractor-title">
            <span>📥 Extrator de PDFs SEI</span>
            <span id="sei-extractor-count" style="font-size: 12px; opacity: 0.8;">0/0</span>
        </div>
        <div id="sei-extractor-progress-bg"><div id="sei-extractor-progress-bar"></div></div>
        <div id="sei-extractor-status">Iniciando análise dos processos da página...</div>
        <div id="sei-extractor-logs"></div>
    `;
    document.body.appendChild(panel);

    const logEl = panel.querySelector('#sei-extractor-logs');
    const barEl = panel.querySelector('#sei-extractor-progress-bar');
    const statusEl = panel.querySelector('#sei-extractor-status');
    const countEl = panel.querySelector('#sei-extractor-count');

    function log(msg, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type === 'error' ? 'log-error' : type === 'warn' ? 'log-warn' : ''}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
        logEl.appendChild(entry);
        logEl.scrollTop = logEl.scrollHeight;
        console.log(`[SEI-Extrator] ${msg}`);
    }

    function updateProgress(current, total, text) {
        const pct = total > 0 ? (current / total) * 100 : 0;
        barEl.style.width = `${pct}%`;
        countEl.textContent = `${current}/${total}`;
        statusEl.textContent = text;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function resolveUrl(url, base) {
        return new URL(url.replace(/&amp;/g, '&'), base).href;
    }

    // 1. Capturar os processos visíveis na caixa
    const linksProcessos = Array.from(document.querySelectorAll('a.processoVisualizado, a.processoNaoVisualizado'));
    const total = linksProcessos.length;

    if (total === 0) {
        log("Nenhum processo encontrado na página atual. Certifique-se de estar na tela da Caixa de Entrada.", "warn");
        statusEl.textContent = "Nenhum processo localizado.";
        return;
    }

    log(`Localizado(s) ${total} processo(s) para download.`);

    for (let i = 0; i < total; i++) {
        let link = linksProcessos[i];
        let processoNumero = link.textContent.trim();
        let urlProcesso = link.href;

        updateProgress(i, total, `Processando: ${processoNumero}`);
        log(`Processo ${processoNumero} (${i + 1}/${total})`);

        try {
            // Passo 1: Acessar a página principal do processo (frameset)
            let resTrabalhar = await fetch(urlProcesso);
            let textTrabalhar = await resTrabalhar.text();

            // Passo 2: Extrair a URL da árvore (ifrArvore)
            let matchArvore = textTrabalhar.match(/src=["']([^"']*acao=arvore_visualizar[^"']*)["']/i);
            if (!matchArvore) {
                log(`Aviso: Frame de árvore não localizado no processo ${processoNumero}`, "warn");
                continue;
            }
            let urlArvore = resolveUrl(matchArvore[1], urlProcesso);

            // Passo 3: Acessar a árvore para achar o botão "Gerar PDF"
            let resArvore = await fetch(urlArvore);
            let textArvore = await resArvore.text();

            let matchPdfUrl = textArvore.match(/href=["']([^"']*acao=procedimento_gerar_pdf[^"']*)["']/i);
            if (!matchPdfUrl) {
                log(`Aviso: Botão "Gerar PDF" não localizado no processo ${processoNumero}`, "warn");
                continue;
            }
            let urlGerarPdf = resolveUrl(matchPdfUrl[1], urlArvore);

            // Passo 4: Fazer o POST para gerar o PDF
            let formData = new URLSearchParams();
            formData.append('hdnInfraTipoPagina', '2');
            formData.append('rdoTipo', 'T');
            formData.append('hdnDocumentosExceto', '');
            formData.append('hdnDocumentosApenas', '');
            formData.append('hdnFlagGerar', '1');

            log(`Gerando PDF no servidor...`);
            let resPostPdf = await fetch(urlGerarPdf, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            let textPost = await resPostPdf.text();

            // Passo 5: Capturar a URL final do arquivo gerado (acao=exibir_arquivo)
            let matchDownloadUrl = textPost.match(/["']([^"']*acao=exibir_arquivo[^"']*)["']/i);
            if (!matchDownloadUrl) {
                log(`Erro: Link final de download não encontrado para ${processoNumero}`, "error");
                continue;
            }
            let urlDownloadFinal = resolveUrl(matchDownloadUrl[1], urlGerarPdf);

            // Passo 6: Acionar download no navegador
            log(`Iniciando download...`);
            let a = document.createElement('a');
            a.href = urlDownloadFinal;
            a.download = `SEI_${processoNumero}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            log(`Sucesso: ${processoNumero} baixado.`, "info");

            // Aguardar intervalo de segurança
            if (i < total - 1) {
                updateProgress(i + 1, total, `Aguardando intervalo de segurança...`);
                await sleep(DELAY_MS);
            }

        } catch (error) {
            log(`Erro ao processar ${processoNumero}: ${error.message}`, "error");
        }
    }

    updateProgress(total, total, "Processamento Concluído!");
    log("Extrator finalizado com sucesso!");
})();