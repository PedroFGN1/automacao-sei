import os
import requests
from typing import Dict, Any, List
from src.core.plugin_base import BasePlugin

class EnviarN8nPlugin(BasePlugin):
    """
    Plugin de integração para enviar PDFs de processos locais para um Webhook ativo do n8n.
    """
    @property
    def id(self) -> str:
        return "enviar_n8n"

    @property
    def name(self) -> str:
        return "Enviador de Processos para n8n"

    @property
    def description(self) -> str:
        return "Busca arquivos PDF correspondentes a processos locais e os envia para um webhook do n8n."

    def get_params_schema(self) -> List[Dict[str, Any]]:
        # Carrega defaults das variáveis de ambiente se disponíveis
        default_webhook = os.getenv("N8N_WEBHOOK_URL", "")
        default_dir = os.getenv("EXPORT_DIR", r"C:\Users\pedro.galvao\Documents\SEI_Exportacoes")
        
        return [
            {
                "name": "lista_processos",
                "label": "Números de Processos (separados por vírgula ou espaço)",
                "type": "text",
                "is_required": True
            },
            {
                "name": "webhook_url",
                "label": "Webhook URL do n8n",
                "type": "text",
                "is_required": True,
                "default_value": default_webhook
            },
            {
                "name": "pasta_pdfs",
                "label": "Diretório de PDFs do SEI",
                "type": "directory",
                "is_required": True,
                "default_value": default_dir
            }
        ]

    def encontrar_pdf_processo(self, numero_processo: str, pasta_pdfs: str) -> str:
        """Busca o PDF na pasta no formato 'numero_processo.pdf' ou 'SEI_numero_processo.pdf'."""
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

    def execute(self, params: Dict[str, Any], logger: Any) -> Dict[str, Any]:
        webhook_url = params["webhook_url"]
        pasta_pdfs = params["pasta_pdfs"]
        
        # Faz parse dos processos digitados pelo usuário
        raw_processos = params["lista_processos"]
        # Substitui vírgulas por espaços e divide
        processos = [p.strip() for p in raw_processos.replace(",", " ").split() if p.strip()]
        
        if not processos:
            raise ValueError("Nenhum número de processo válido fornecido.")
            
        logger(f"Iniciando processamento para envio de {len(processos)} processos ao n8n...", "INFO")
        logger(f"Webhook URL: {webhook_url}", "INFO")
        logger(f"Diretório de PDFs: {pasta_pdfs}", "INFO")
        
        sucessos = 0
        falhas = 0
        
        for idx, num_proc in enumerate(processos, 1):
            logger(f"[{idx}/{len(processos)}] Processando processo: {num_proc}...", "INFO")
            
            caminho_pdf = self.encontrar_pdf_processo(num_proc, pasta_pdfs)
            if not caminho_pdf:
                logger(f"  [AVISO] Arquivo PDF para o processo {num_proc} não foi encontrado na pasta.", "WARNING")
                falhas += 1
                continue
                
            nome_arquivo = os.path.basename(caminho_pdf)
            
            try:
                with open(caminho_pdf, 'rb') as f:
                    files = {
                        'file': (nome_arquivo, f, 'application/pdf')
                    }
                    data = {
                        'numero_processo': num_proc,
                        'data_envio': nome_arquivo
                    }
                    
                    resposta = requests.post(webhook_url, files=files, data=data, timeout=30)
                    
                    if resposta.status_code in [200, 201, 202]:
                        logger(f"  [SUCESSO] Processo {num_proc} enviado com sucesso (Status {resposta.status_code})", "INFO")
                        sucessos += 1
                    else:
                        logger(f"  [ERRO] Falha no envio do processo {num_proc} (Status {resposta.status_code})", "ERROR")
                        logger(f"  Resposta do servidor: {resposta.text[:200]}", "ERROR")
                        falhas += 1
                        
            except Exception as e:
                logger(f"  [ERRO] Falha de conexão/leitura para {num_proc}: {str(e)}", "ERROR")
                falhas += 1
                
        logger(f"Envio finalizado. Sucessos: {sucessos}, Falhas: {falhas}.", "INFO")
        
        return {
            "status": "concluido",
            "sucessos": sucessos,
            "falhas": falhas
        }
