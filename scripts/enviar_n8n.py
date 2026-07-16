#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enviador de Processos SEI para o n8n
Autor: Antigravity AI
Descrição: Script modular que busca arquivos PDF de processos e os envia individualmente
           como binários via multipart/form-data para um Webhook ativo do n8n.
"""

import os
import sys
import argparse
import requests
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Carrega configurações do arquivo .env (se disponível) ou usa variáveis de ambiente do sistema
load_dotenv()

# === CONFIGURAÇÕES GERAIS ===
DEFAULT_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
DEFAULT_EXPORT_DIR = os.getenv("EXPORT_DIR", r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes")
DEFAULT_PROMPT = os.getenv("N8N_PROMPT", "Analise os seguintes documentos e retorne uma análise completa.")


# Cores do terminal
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'


def encontrar_pdf_processo(numero_processo, pasta_pdfs):
    """
    Procura o arquivo PDF correspondente ao número de processo na pasta.
    Suporta os formatos 'numero_processo.pdf' e 'SEI_numero_processo.pdf'.
    Retorna o caminho absoluto do arquivo ou None se não encontrado.
    """
    if not os.path.exists(pasta_pdfs):
        return None
        
    candidatos = [
        f"{numero_processo}.pdf",
        f"{numero_processo}.PDF",
        f"SEI_{numero_processo}.pdf",
        f"SEI_{numero_processo}.PDF"
    ]
    
    for nome_arq in candidatos:
        caminho_completo = os.path.join(pasta_pdfs, nome_arq)
        if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
            return caminho_completo
            
    return None


def enviar_processos_n8n(lista_processos, webhook_url=None, pasta_pdfs=None):
    """
    Função principal que busca os PDFs e faz a requisição POST para o webhook do n8n.
    """
    url = webhook_url or DEFAULT_WEBHOOK_URL
    pasta = pasta_pdfs or DEFAULT_EXPORT_DIR
    
    if not url:
        print(f"{Cores.VERMELHO}[ERRO] URL do webhook do n8n não configurada no .env ou parâmetros.{Cores.RESET}")
        return False
        
    if not os.path.exists(pasta):
        print(f"{Cores.VERMELHO}[ERRO] Diretório de PDFs '{pasta}' não existe.{Cores.RESET}")
        return False
        
    print(f"{Cores.NEGRITO}[*] Iniciando envio de {len(lista_processos)} processos para o n8n...{Cores.RESET}")
    print(f"[*] Webhook: {url}")
    print(f"[*] Diretório de PDFs: {pasta}\n")
    
    sucessos = 0
    falhas = 0
    
    for idx, num_proc in enumerate(lista_processos, 1):
        num_proc = num_proc.strip()
        if not num_proc:
            continue
            
        print(f"[{idx}/{len(lista_processos)}] Processando processo: {num_proc}...", end="", flush=True)
        
        caminho_pdf = encontrar_pdf_processo(num_proc, pasta)
        if not caminho_pdf:
            print(f" {Cores.AMARELO}[NÃO ENCONTRADO - Arquivo PDF ausente na pasta]{Cores.RESET}")
            falhas += 1
            continue
            
        nome_arquivo = os.path.basename(caminho_pdf)
        
        try:
            # Abre o arquivo em modo binário
            with open(caminho_pdf, 'rb') as f:
                # Prepara o anexo (multipart/form-data) e dados adicionais
                files = {
                    'file': (nome_arquivo, f, 'application/pdf')
                }
                data = {
                    'numero_processo': num_proc,
                    'data_envio': requests.utils.quote(nome_arquivo) # Informações extras se necessário
                }
                
                # Envia via POST
                resposta = requests.post(url, files=files, data=data, timeout=30)
                
                # O n8n costuma responder com status 200, 201 ou 202
                if resposta.status_code in [200, 201, 202]:
                    print(f" {Cores.VERDE}[ENVIADO COM SUCESSO - Status {resposta.status_code}]{Cores.RESET}")
                    sucessos += 1
                else:
                    print(f" {Cores.VERMELHO}[FALHA NO ENVIO - Status {resposta.status_code}]{Cores.RESET}")
                    print(f"    Resposta do Servidor: {resposta.text[:200]}")
                    falhas += 1
                    
        except Exception as e:
            print(f" {Cores.VERMELHO}[FALHA - Erro de conexão/leitura: {str(e)}]{Cores.RESET}")
            falhas += 1
            
    print(f"\n{Cores.NEGRITO}=== Relatório de Envio n8n ==={Cores.RESET}")
    print(f"{Cores.VERDE}✓ Enviados com sucesso: {sucessos}{Cores.RESET}")
    print(f"{Cores.VERMELHO}✗ Falhas de envio: {falhas}{Cores.RESET}")
    print(f"==============================\n")
    
    return sucessos > 0


def main():
    parser = argparse.ArgumentParser(
        description="Envia PDFs de processos para um webhook do n8n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "processos",
        nargs="+",
        help="Lista de números de processos a serem enviados (separados por espaço)"
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        help="URL do webhook do n8n. Se omitido, usa a do arquivo .env."
    )
    
    parser.add_argument(
        "-d", "--dir",
        type=str,
        help="Diretório onde os arquivos PDF estão salvos. Se omitido, usa o do arquivo .env."
    )
    
    args = parser.parse_args()
    
    # Ativa suporte a cores ANSI no console do Windows
    if sys.platform.startswith('win'):
        os.system('color')
        
    enviar_processos_n8n(args.processos, webhook_url=args.url, pasta_pdfs=args.dir)


if __name__ == "__main__":
    main()
