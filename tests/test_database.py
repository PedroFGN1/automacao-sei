import os
import pytest
import core.database as db

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Configura um banco de dados de teste isolado e limpa as tabelas antes de cada teste.
    """
    original_db = db.DB_FILE
    db.DB_FILE = "test_automacao.db"
    db.inicializar_banco()
    
    # Limpa a tabela processos para isolar os testes
    with db.obter_conexao() as conn:
        conn.cursor().execute("DELETE FROM processos")
        conn.commit()
        
    yield
    
    # Limpa a tabela após o teste
    try:
        with db.obter_conexao() as conn:
            conn.cursor().execute("DELETE FROM processos")
            conn.commit()
    except Exception:
        pass
        
    db.DB_FILE = original_db

def test_salvar_processo_novo():
    # Insere novo processo
    assert db.salvar_processo("12345/2026", "Tipo A", "PENDENTE", "Sem detalhes")
    
    # Verifica persistência
    processos = db.obter_processos_paginados(pagina=1, itens_por_pagina=10)
    assert len(processos) == 1
    assert processos[0]["numero"] == "12345/2026"
    assert processos[0]["tipo"] == "Tipo A"
    assert processos[0]["status"] == "PENDENTE"
    assert processos[0]["detalhes"] == "Sem detalhes"

def test_salvar_processo_atualizacao():
    db.salvar_processo("12345/2026", "Tipo A", "PENDENTE")
    
    # Atualiza status e detalhes
    db.salvar_processo("12345/2026", "Tipo A", "PROCESSADO", "Concluído com sucesso")
    
    processos = db.obter_processos_paginados(pagina=1, itens_por_pagina=10)
    assert len(processos) == 1
    assert processos[0]["status"] == "PROCESSADO"
    assert processos[0]["detalhes"] == "Concluído com sucesso"

def test_paginacao_e_filtros():
    # Insere 15 processos para testar paginação
    for i in range(1, 16):
        db.salvar_processo(f"N-{i}", f"Tipo {i}", "PENDENTE")
        
    # Insere alguns com status diferente
    db.salvar_processo("ESPECIAL-1", "Licença", "PROCESSADO")
    db.salvar_processo("ESPECIAL-2", "Licença", "ERRO")
    
    # Testa total geral de processos
    assert db.obter_total_processos() == 17
    
    # Testa total com filtro de status
    assert db.obter_total_processos(filtro_status="PROCESSADO") == 1
    
    # Testa busca textual
    assert db.obter_total_processos(busca="ESPECIAL") == 2
    
    # Testa itens da página 1 (tamanho 10)
    pagina_1 = db.obter_processos_paginados(pagina=1, itens_por_pagina=10)
    assert len(pagina_1) == 10
    
    # Testa itens da página 2 (deve conter os 7 restantes)
    pagina_2 = db.obter_processos_paginados(pagina=2, itens_por_pagina=10)
    assert len(pagina_2) == 7
