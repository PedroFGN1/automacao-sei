import pytest
import requests
from unittest.mock import patch, MagicMock
from core.n8n_client import enviar_para_ia

def test_arquivo_nao_encontrado():
    with pytest.raises(FileNotFoundError):
        enviar_para_ia("http://webhook.com", "caminho_inexistente.pdf", "Extraia os dados")

@patch("core.n8n_client.requests.post")
@patch("core.n8n_client.os.path.exists")
def test_envio_com_sucesso(mock_exists, mock_post):
    # Simula que o arquivo existe
    mock_exists.return_value = True
    
    # Cria mock de resposta bem-sucedida com JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "processo": "123"}
    mock_post.return_value = mock_response
    
    # Executa a chamada abrindo um arquivo fictício temporário criado em RAM
    # Para evitar abrir arquivo real, vamos simular o open no patch
    with patch("core.n8n_client.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value = b"dados_pdf"
        
        resultado = enviar_para_ia("http://webhook.com", "teste.pdf", "Extraia os dados")
        
        assert resultado == {"status": "ok", "processo": "123"}
        mock_post.assert_called_once()
        
        # Verifica argumentos passados para requests.post
        args, kwargs = mock_post.call_args
        assert args[0] == "http://webhook.com"
        assert "files" in kwargs
        assert "prompt" in kwargs["data"]
        assert kwargs["data"]["prompt"] == "Extraia os dados"

@patch("core.n8n_client.requests.post")
@patch("core.n8n_client.os.path.exists")
def test_falha_de_rede_http(mock_exists, mock_post):
    mock_exists.return_value = True
    
    # Simula falha levantada pelo raise_for_status()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Erro 500")
    mock_post.return_value = mock_response
    
    with patch("core.n8n_client.open", create=True):
        with pytest.raises(requests.exceptions.RequestException):
            enviar_para_ia("http://webhook.com", "teste.pdf", "Extraia")

@patch("core.n8n_client.requests.post")
@patch("core.n8n_client.os.path.exists")
def test_resposta_json_invalido(mock_exists, mock_post):
    mock_exists.return_value = True
    
    # Resposta com texto que não é JSON válido
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("JSON inválido")
    mock_post.return_value = mock_response
    
    with patch("core.n8n_client.open", create=True):
        with pytest.raises(ValueError) as exc:
            enviar_para_ia("http://webhook.com", "teste.pdf", "Extraia")
        assert "não-JSON" in str(exc.value)
