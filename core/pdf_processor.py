import os
from pypdf import PdfReader

def extrair_texto_pdf(pdf_path: str) -> str:
    """
    Lê um arquivo PDF do caminho fornecido e extrai todo o seu texto.
    
    Parâmetros:
      - pdf_path: Caminho absoluto ou relativo para o arquivo PDF.
      
    Retorna:
      - String contendo o texto completo do PDF.
      
    Lança:
      - FileNotFoundError se o arquivo não existir.
      - Exception em caso de erro na leitura ou arquivo corrompido.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
    try:
        reader = PdfReader(pdf_path)
        texto_completo = []
        
        for pagina in reader.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo.append(texto_pagina)
                
        return "\n".join(texto_completo)
    except Exception as exc:
        raise Exception(f"Erro ao extrair texto do PDF {pdf_path}: {str(exc)}")
