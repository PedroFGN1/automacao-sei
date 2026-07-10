if (!localStorage.getItem('processosSEI')) {
    localStorage.setItem('processosSEI', JSON.stringify([]));
}

function capturarProcessosPermanente() {
    // Recupera o que já foi salvo antes
    let acumulados = JSON.parse(localStorage.getItem('processosSEI'));
    
    // Captura os processos da página atual no SEI 5.0.4
    const elementos = document.querySelectorAll('a.processoVisualizado, a.processoNaoVisualizado');
    let contagemNovos = 0;

    elementos.forEach(link => {
        const numero = link.textContent.trim();
        if (numero && !acumulados.includes(numero)) {
            acumulados.push(numero);
            contagemNovos++;
        }
    });

    // Salva a lista atualizada de volta na localStorage
    localStorage.setItem('processosSEI', JSON.stringify(acumulados));

    console.log(`%c[SEI SCRAPER] +${contagemNovos} novos processos capturados nesta página.`, 'color: #2ed573; font-weight: bold;');
    console.log(`%c[SEI SCRAPER] Total salvo no navegador: ${acumulados.length} processos.`, 'color: #1e90ff; font-weight: bold;');
    console.log('%c👉 Mude de página e cole este comando novamente para continuar acumulando!', 'color: #ffa500;');
}

// Funções utilitárias que ficam disponíveis para você usar a qualquer momento:

window.copiarLista = function() {
    let acumulados = JSON.parse(localStorage.getItem('processosSEI')) || [];
    if (acumulados.length === 0) {
        console.warn("Nenhum processo salvo ainda.");
        return;
    }
    copy(acumulados.join('\n'));
    console.log(`%c[SUCESSO] ${acumulados.length} processos copiados para a área de transferência!`, 'color: #2ed573; font-weight: bold;');
};

window.limparLista = function() {
    localStorage.removeItem('processosSEI');
    console.log("%c[ZAP] Memória local limpa com sucesso. Pronto para recomeçar.", "color: #ff4757; font-weight: bold;");
};

// Executa a primeira captura automaticamente
capturarProcessosPermanente();