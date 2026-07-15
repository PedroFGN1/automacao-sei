import time
from typing import Dict, Any, List
from src.core.plugin_base import BasePlugin

class DummyPlugin(BasePlugin):
    """
    Plugin de demonstração e teste para validar a renderização dinâmica da UI
    e a execução assíncrona com passagem de parâmetros.
    """
    @property
    def id(self) -> str:
        return "dummy_robot"

    @property
    def name(self) -> str:
        return "Robô de Teste Dinâmico"

    @property
    def description(self) -> str:
        return "Um plugin dummy para validar inputs, logs em tempo real e geração de arquivos Excel/CSV."

    def get_params_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "nome_operador",
                "label": "Nome do Operador",
                "type": "text",
                "is_required": True,
                "default_value": "Operador Padrão"
            },
            {
                "name": "senha_sei",
                "label": "Senha de Acesso",
                "type": "password",
                "is_required": True
            },
            {
                "name": "planilha_processos",
                "label": "Planilha de Processos (Excel/CSV)",
                "type": "file",
                "is_required": False,
                "allowed_extensions": [".xlsx", ".csv"]
            },
            {
                "name": "pasta_destino",
                "label": "Pasta de Destino das Exportações",
                "type": "directory",
                "is_required": True,
                "default_value": "C:\\SEI_Exportacoes"
            },
            {
                "name": "gerar_planilha_saida",
                "label": "Gerar Planilha de Resultados",
                "type": "bool",
                "is_required": False,
                "default_value": True
            }
        ]

    def execute(self, params: Dict[str, Any], logger: Any) -> Dict[str, Any]:
        logger("Iniciando a simulação de automação...", "INFO")
        logger(f"Operador ativo: {params.get('nome_operador')}", "INFO")
        logger(f"Modo silencioso (Headless): {params.get('headless')}", "INFO")
        logger(f"Pasta de destino configurada: {params.get('pasta_destino')}", "INFO")
        
        # Simula processamento em etapas para validar log em tempo real
        total_etapas = 5
        for i in range(1, total_etapas + 1):
            time.sleep(1)  # Simula tempo de processamento
            logger(f"Etapa {i}/{total_etapas} concluída.", "INFO")
            
        if params.get("gerar_planilha_saida"):
            logger("Gerando planilha Excel de resultados simulados...", "WARNING")
            time.sleep(0.5)
            
        logger("Simulação concluída com sucesso!", "INFO")
        
        return {
            "status": "sucesso",
            "etapas_processadas": total_etapas,
            "operador": params.get("nome_operador")
        }
