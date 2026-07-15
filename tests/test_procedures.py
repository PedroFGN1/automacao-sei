import pytest
from procedures import PROCEDURES, carregar_procedimentos_dinamicamente

def test_descoberta_procedimentos():
    # Recarrega para garantir que os módulos sejam scaneados
    carregar_procedimentos_dinamicamente()
    
    # O ExportadorSei deve estar na lista de procedimentos carregados
    assert "ExportadorSei" in PROCEDURES
    
    # O tipo do objeto mapeado deve ser a classe correspondente
    classe_exportador = PROCEDURES["ExportadorSei"]
    assert hasattr(classe_exportador, "fixed_settings")
    assert hasattr(classe_exportador, "variable_settings")
    assert hasattr(classe_exportador, "run")

def test_configuracoes_exportador():
    Exportador = PROCEDURES["ExportadorSei"]
    instancia = Exportador()
    
    # Testa configurações fixas
    fixed = instancia.fixed_settings
    assert isinstance(fixed, dict)
    assert "sei_url" in fixed
    assert fixed["sei_url"]["type"] == "string"
    
    # Testa configurações variáveis
    variable = instancia.variable_settings
    assert isinstance(variable, dict)
    assert "caminho_planilha" in variable
    assert variable["caminho_planilha"]["type"] == "path"

def test_execucao_exportador_com_erro():
    Exportador = PROCEDURES["ExportadorSei"]
    instancia = Exportador()
    
    logs = []
    def log_cb(msg):
        logs.append(msg)
        
    # Sem planilha, a automação deve retornar False
    sucesso = instancia.run(settings={"sei_url": "http://teste.com"}, log_callback=log_cb)
    assert sucesso is False
    assert any("Erro: Planilha de entrada" in log for log in logs)

def test_execucao_exportador_com_sucesso():
    Exportador = PROCEDURES["ExportadorSei"]
    instancia = Exportador()
    
    logs = []
    def log_cb(msg):
        logs.append(msg)
        
    settings = {
        "sei_url": "http://teste.com",
        "usuario": "usuario_teste",
        "caminho_planilha": "C:/documentos/processos.xlsx"
    }
    
    sucesso = instancia.run(settings=settings, log_callback=log_cb)
    assert sucesso is True
    assert any("Iniciando procedimento" in log for log in logs)
    assert any("Conectando à URL: http://teste.com" in log for log in logs)
    assert any("Logado como: usuario_teste" in log for log in logs)
    assert any("Processando linha 3/3" in log for log in logs)
    assert any("concluído com sucesso!" in log for log in logs)
