#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Indexador de PDFs do SEI
Autor: Antigravity AI
Descrição: Script Python para ler em massa arquivos PDF de processos do SEI,
           extrair o texto de forma eficiente (página por página) e armazenar
           estruturadamente em um banco de dados local SQLite (automacao.db).
           Inclui também um módulo de busca rápida com contexto.
Execução: python indexador_pdf.py --dir path --search "Ação Civil Pública"
"""

import os
import sys
import re
import sqlite3
import argparse
from datetime import datetime
# pyrefly: ignore [missing-import]
import pypdf

# === CONFIGURAÇÕES PADRÃO ===
DB_FILE = r"C:\Users\pedro.galvao\Documents\automacao.db"
DEFAULT_EXPORT_DIR = r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes"

# Códigos ANSI para colorir logs no console
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'


def inicializar_banco():
    """ Inicializa as tabelas necessárias no banco SQLite e cria índices. """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Habilita o suporte a chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Cria a tabela de processos_texto se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processos_texto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT NOT NULL,
            texto_completo TEXT,
            data_processamento TEXT NOT NULL,
            FOREIGN KEY (numero_processo) REFERENCES processos (numero_processo) ON DELETE CASCADE
        );
    """)
    
    # Cria um índice para otimizar buscas por número de processo
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_processos_texto_numero 
        ON processos_texto (numero_processo);
    """)
    
    conn.commit()
    conn.close()


def extrair_texto_pdf(caminho_pdf):
    """
    Extrai o texto de um PDF página por página para evitar estouro de memória RAM.
    Retorna uma string com o texto completo ou "[PDF_DIGITALIZADO_SEM_TEXTO_NATIVO]" se não houver texto.
    """
    texto_paginas = []
    
    with open(caminho_pdf, 'rb') as f:
        reader = pypdf.PdfReader(f)
        
        # Extração sequencial eficiente de cada página
        for i, pagina in enumerate(reader.pages):
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_paginas.append(texto_extraido)
                
    texto_completo = "\n".join(texto_paginas).strip()
    
    # Retorna string indicando PDF sem texto de máquina caso esteja vazio
    if not texto_completo:
        return "[PDF_DIGITALIZADO_SEM_TEXTO_NATIVO]"
        
    return texto_completo


def garantir_processo_no_banco(conn, numero_processo):
    """
    Garante que o processo existe na tabela principal 'processos'.
    Se não existir, insere-o com status 'BAIXADO' para respeitar a chave estrangeira.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processos WHERE numero_processo = ?", (numero_processo,))
    existe = cursor.fetchone()
    
    if not existe:
        timestamp_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO processos (numero_processo, status, tentativas, ultima_execucao)
            VALUES (?, 'BAIXADO', 1, ?)
        """, (numero_processo, timestamp_atual))
        conn.commit()
        print(f"{Cores.AMARELO}[*] Processo {numero_processo} não constava na tabela 'processos'. Adicionado com status 'BAIXADO'.{Cores.RESET}")


def indexar_pasta(caminho_pasta):
    """ Varre a pasta fornecida em busca de PDFs do SEI e indexa-os no SQLite. """
    if not os.path.exists(caminho_pasta):
        print(f"{Cores.VERMELHO}[ERRO] O diretório '{caminho_pasta}' não existe.{Cores.RESET}")
        return

    # Listar todos os arquivos da pasta
    arquivos = os.listdir(caminho_pasta)
    
    # Regex para capturar arquivos no formato SEI_{numero_processo}.pdf ou {numero_processo}.pdf
    # O padrão é tolerante a variações, capturando o número de processo
    padrao_sei = re.compile(r"^(?:SEI_)?(\d+)\.pdf$", re.IGNORECASE)
    
    pdfs_para_processar = []
    for arq in arquivos:
        match = padrao_sei.match(arq)
        if match:
            numero_processo = match.group(1)
            caminho_completo = os.path.join(caminho_pasta, arq)
            pdfs_para_processar.append((numero_processo, caminho_completo))
            
    total_encontrados = len(pdfs_para_processar)
    if total_encontrados == 0:
        print(f"{Cores.AMARELO}[!] Nenhum PDF no padrão 'SEI_{{numero_processo}}.pdf' foi encontrado em '{caminho_pasta}'.{Cores.RESET}")
        return

    print(f"{Cores.NEGRITO}[*] Iniciando indexação de {total_encontrados} arquivos PDF...{Cores.RESET}\n")

    conn = sqlite3.connect(DB_FILE)
    # Habilitar chaves estrangeiras na conexão atual
    conn.execute("PRAGMA foreign_keys = ON;")
    
    sucessos = 0
    ignorados = 0
    falhas = 0

    for idx, (num_processo, caminho_pdf) in enumerate(pdfs_para_processar, 1):
        # Exibe progresso no terminal
        pct = (idx / total_encontrados) * 100
        print(f"[{idx}/{total_encontrados} - {pct:.1f}%] Processo: {num_processo}...", end="", flush=True)

        try:
            # 1. Verifica se já está indexado
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processos_texto WHERE numero_processo = ?", (num_processo,))
            ja_indexado = cursor.fetchone()

            if ja_indexado:
                print(f" {Cores.AMARELO}[Ignorado - Já Indexado]{Cores.RESET}")
                ignorados += 1
                continue

            # 2. Garante o processo na tabela 'processos' para evitar quebra de Foreign Key
            garantir_processo_no_banco(conn, num_processo)

            # 3. Extrai o texto do PDF
            texto_extraido = extrair_texto_pdf(caminho_pdf)

            # 4. Salva no banco de dados processos_texto
            timestamp_processamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO processos_texto (numero_processo, texto_completo, data_processamento)
                VALUES (?, ?, ?)
            """, (num_processo, texto_extraido, timestamp_processamento))
            conn.commit()

            print(f" {Cores.VERDE}[Sucesso]{Cores.RESET}")
            sucessos += 1

        except Exception as e:
            print(f" {Cores.VERMELHO}[FALHA - {str(e)}]{Cores.RESET}")
            falhas += 1

    conn.close()

    # Relatório final
    print(f"\n{Cores.NEGRITO}=== Relatório de Indexação ==={Cores.RESET}")
    print(f"{Cores.VERDE}[OK] Processados com Sucesso: {sucessos}{Cores.RESET}")
    print(f"{Cores.AMARELO}[Ignorado] Ignorados (Já Indexados): {ignorados}{Cores.RESET}")
    if falhas > 0:
        print(f"{Cores.VERMELHO}[FALHA] Falhas na extração: {falhas}{Cores.RESET}")
    else:
        print(f"{Cores.VERDE}[FALHA] Falhas na extração: {falhas}{Cores.RESET}")
    print(f"=============================\n")


def buscar_palavras_chave(termos_busca):
    """
    Busca por palavras-chave na tabela processos_texto usando a cláusula LIKE.
    Retorna resultados detalhados destacando trechos do texto.
    """
    if not os.path.exists(DB_FILE):
        print(f"{Cores.VERMELHO}[ERRO] O banco de dados '{DB_FILE}' não foi encontrado. Execute a indexação primeiro.{Cores.RESET}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"{Cores.NEGRITO}[*] Buscando registros que contêm: {', '.join([f'\"{t}\"' for t in termos_busca])}...{Cores.RESET}\n")

    # Monta a query dinâmica com cláusulas LIKE ligadas por OR
    # Exemplo: texto_completo LIKE ? OR texto_completo LIKE ? ...
    clausulas = " OR ".join(["texto_completo LIKE ?" for _ in termos_busca])
    query = f"""
        SELECT numero_processo, texto_completo 
        FROM processos_texto 
        WHERE {clausulas}
    """
    
    # Prepara os parâmetros com os curingas '%'
    parametros = [f"%{termo}%" for termo in termos_busca]
    
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()

    if not resultados:
        print(f"{Cores.AMARELO}[!] Nenhuma ocorrência dos termos informados foi encontrada no banco de dados.{Cores.RESET}")
        conn.close()
        return []

    print(f"{Cores.VERDE}[OK] Encontrado(s) {len(resultados)} processo(s) correspondente(s):{Cores.RESET}\n")

    for num_processo, texto in resultados:
        print(f"{Cores.NEGRITO}Processo: {num_processo}{Cores.RESET}")
        
        # Procura onde estão localizados os termos de busca para extrair um trecho
        trecho_encontrado = None
        for termo in termos_busca:
            # Procura de forma case-insensitive
            match = re.search(re.escape(termo), texto, re.IGNORECASE)
            if match:
                inicio_match = match.start()
                fim_match = match.end()
                
                # Extrai 100 caracteres antes e 100 depois da ocorrência
                inicio_trecho = max(0, inicio_match - 100)
                fim_trecho = min(len(texto), fim_match + 100)
                
                trecho_cru = texto[inicio_trecho:fim_trecho]
                # Limpa quebras de linha para exibição amigável em uma única linha no console
                trecho_limpo = " ".join(trecho_cru.split())
                
                # Destaca a palavra pesquisada na string
                termo_encontrado = trecho_cru[inicio_match - inicio_trecho : fim_match - inicio_trecho]
                trecho_destacado = trecho_limpo.replace(
                    termo_encontrado, 
                    f"{Cores.NEGRITO}{Cores.VERDE}{termo_encontrado}{Cores.RESET}"
                )
                
                trecho_encontrado = f"... {trecho_destacado} ..."
                break
        
        if trecho_encontrado:
            print(f"  Trecho: {trecho_encontrado}")
        else:
            # Se for PDF sem texto ou se falhou a localização direta
            print(f"  Trecho: [Texto completo marcado como digitalizado ou indisponível]")
            
        print("-" * 50)

    conn.close()
    return [row[0] for row in resultados]


def main():
    parser = argparse.ArgumentParser(
        description="Indexador e Buscador de Textos de PDFs do SEI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-d", "--dir",
        type=str,
        default=DEFAULT_EXPORT_DIR,
        help=f"Diretório onde os arquivos PDF estão salvos. (Padrão: {DEFAULT_EXPORT_DIR})"
    )
    
    parser.add_argument(
        "-s", "--search",
        type=str,
        help="Termo ou palavra-chave para buscar no banco de dados. Se fornecido, o script não indexará novos PDFs."
    )
    
    parser.add_argument(
        "--n8n",
        action="store_true",
        help="Envia os PDFs dos processos encontrados na busca para o webhook do n8n."
    )

    args = parser.parse_args()

    # Inicializa a estrutura do banco SQLite
    inicializar_banco()

    processos_encontrados = []

    if args.search:
        # Se passar o argumento de busca, realiza apenas a busca
        processos_encontrados = buscar_palavras_chave([args.search])
    else:
        # Modo padrão: indexa a pasta e depois executa os testes de busca especificados no prompt
        indexar_pasta(args.dir)
        
        #print(f"{Cores.NEGRITO}=== Executando Busca Demonstrativa (Requisito Módulo Extra) ==={Cores.RESET}")
        #termos_demonstrativos = ['Ação Civil Pública', 'ACP', 'Ministério Público']
        #processos_encontrados = buscar_palavras_chave(termos_demonstrativos)
        
    if args.n8n and processos_encontrados:
        try:
            from enviar_n8n import enviar_processos_n8n
            enviar_processos_n8n(processos_encontrados, pasta_pdfs=args.dir)
        except Exception as ne:
            print(f"{Cores.VERMELHO}[ERRO] Falha ao executar o envio para o n8n: {ne}{Cores.RESET}")


if __name__ == "__main__":
    # Garante suporte a cores ANSI no console do Windows (se aplicável)
    if sys.platform.startswith('win'):
        os.system('color')
        
    main()
