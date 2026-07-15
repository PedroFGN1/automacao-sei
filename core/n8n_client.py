import os
import requests

def enviar_para_ia(webhook_url: str, arquivo_path: str, prompt: str) -> dict:
    """
    Envia um arquivo local e uma instrução de prompt para um webhook do n8n,
    retornando o resultado estruturado processado pela IA.
    
    Parâmetros:
      - webhook_url: URL HTTP do webhook ativo do n8n.
      - arquivo_path: Caminho local do arquivo (ex: PDF ou imagem).
      - prompt: Instrução em texto com as diretrizes de processamento para a IA.
      
    Retorna:
      - Dicionário Python representando a resposta JSON estruturada do n8n.
      
    Lança:
      - FileNotFoundError se o arquivo de entrada não existir.
      - requests.exceptions.RequestException em caso de falhas de conexão/timeout HTTP.
      - ValueError se a resposta do webhook não for um JSON válido.
    """
    if not os.path.exists(arquivo_path):
        raise FileNotFoundError(f"Arquivo não localizado para envio: {arquivo_path}")
        
    nome_arquivo = os.path.basename(arquivo_path)
    
    try:
        # Abre o arquivo de forma genérica binária para envio
        with open(arquivo_path, "rb") as file_handle:
            files = {
                "file": (nome_arquivo, file_handle, "application/octet-stream")
            }
            data = {
                "prompt": prompt
            }
            
            # Executa requisição POST com timeout de 30 segundos
            response = requests.post(webhook_url, files=files, data=data, timeout=30)
            
            # Levanta exceção se o código de status for de erro (4xx/5xx)
            response.raise_for_status()
            
            # Converte a resposta em dicionário Python
            return response.json()
            
    except requests.exceptions.RequestException as req_exc:
        # Encapsula ou repassa erros de transporte HTTP e de rede
        raise requests.exceptions.RequestException(
            f"Falha de comunicação de rede com o webhook do n8n: {str(req_exc)}"
        )
    except ValueError as json_exc:
        raise ValueError(
            f"O webhook do n8n retornou uma resposta em formato inválido (não-JSON): {str(json_exc)}"
        )
