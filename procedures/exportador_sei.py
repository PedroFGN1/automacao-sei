from core.base_procedure import BaseProcedure
import time

class ExportadorSei(BaseProcedure):
    """
    Procedimento de automação de exemplo para exportação de dados do SEI.
    """

    @property
    def fixed_settings(self) -> dict:
        return {
            "sei_url": {
                "label": "URL do SEI",
                "type": "string",
                "default": "https://sei.economia.gov.br",
                "description": "URL principal do portal SEI da instituição"
            },
            "usuario": {
                "label": "Usuário SEI",
                "type": "string",
                "default": "",
                "description": "Nome de login de acesso ao SEI"
            },
            "senha": {
                "label": "Senha",
                "type": "password",
                "default": "",
                "description": "Senha de acesso do usuário"
            }
        }

    @property
    def variable_settings(self) -> dict:
        return {
            "caminho_planilha": {
                "label": "Planilha Excel (Entrada)",
                "type": "path",
                "default": "",
                "description": "Caminho completo do arquivo Excel (.xlsx) contendo processos"
            },
            "salvar_pdf": {
                "label": "Exportar em PDF",
                "type": "string",
                "default": "Sim",
                "description": "Define se o sistema deve gerar arquivos PDF das peças"
            }
        }

    def run(self, settings: dict, log_callback) -> bool:
        log_callback("Iniciando procedimento de exportação do SEI...")
        
        # Recupera as configurações passadas
        sei_url = settings.get("sei_url", "https://sei.economia.gov.br")
        usuario = settings.get("usuario", "")
        caminho_planilha = settings.get("caminho_planilha", "")
        
        log_callback(f"Conectando à URL: {sei_url}")
        if not usuario:
            log_callback("Aviso: Usuário de login não foi preenchido.")
        else:
            log_callback(f"Logado como: {usuario}")
            
        if not caminho_planilha:
            log_callback("Erro: Planilha de entrada não configurada.")
            return False
            
        # Simula a execução da automação
        log_callback(f"Lendo processos da planilha: {caminho_planilha}")
        time.sleep(0.5)
        
        log_callback("Processando linha 1/3: Processo 52100.003412/2026-11")
        time.sleep(0.3)
        log_callback("Extraindo dados do processo ambiental...")
        
        log_callback("Processando linha 2/3: Processo 52100.003415/2026-44")
        time.sleep(0.3)
        log_callback("Fazendo o download de anexos do processo...")
        
        log_callback("Processando linha 3/3: Processo 52100.003417/2026-66")
        time.sleep(0.3)
        log_callback("Salvando histórico de trâmites do processo...")
        
        log_callback("Procedimento de exportação concluído com sucesso!")
        return True
