from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable

class BasePlugin(ABC):
    """
    Interface formal que todos os robôs de automação (plugins) devem implementar.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Retorna o identificador interno único do plugin."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome amigável do robô a ser exibido no menu/combobox da UI."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Retorna a descrição de negócio do robô para explicar o que ele faz."""
        pass

    @abstractmethod
    def get_params_schema(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de dicionários definindo os parâmetros necessários.
        Cada dicionário deve seguir a estrutura:
        {
            "name": str,                  # nome da chave no dicionário de argumentos
            "label": str,                 # rótulo exibido na UI
            "type": str,                  # 'text', 'password', 'file', 'directory', 'bool'
            "is_required": bool,          # se o preenchimento é obrigatório
            "default_value": Any,         # valor padrão opcional
            "allowed_extensions": list    # opcional para type='file' (ex: ['.xlsx', '.csv'])
        }
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any], logger: Callable[[str, str], None]) -> Dict[str, Any]:
        """
        Ponto de entrada da execução do robô. Será executado em uma thread secundária.
        
        Args:
            params: Dicionário contendo os valores preenchidos na interface.
            logger: Função callback para registrar logs em tempo real na UI.
                    Assinatura: logger(mensagem, nivel) com nivel em ['INFO', 'WARNING', 'ERROR'].
                    
        Returns:
            Dicionário com o resultado final da execução.
        """
        pass
