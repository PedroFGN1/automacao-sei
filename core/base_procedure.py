from abc import ABC, abstractmethod

class BaseProcedure(ABC):
    """
    Classe base abstrata para todos os procedimentos de automação (plugins).
    """

    @property
    @abstractmethod
    def fixed_settings(self) -> dict:
        """
        Retorna a especificação das configurações estáticas exigidas pelo procedimento.
        Retorna um dicionário com o formato:
        {
            "CAMPO_ID": {
                "label": "Rótulo do Campo",
                "type": "string" | "path" | "password",
                "default": "valor_padrao",
                "description": "Texto explicativo"
            }
        }
        """
        pass

    @property
    @abstractmethod
    def variable_settings(self) -> dict:
        """
        Retorna a especificação das configurações variáveis exigidas pelo procedimento.
        Retorna um dicionário com o mesmo formato de fixed_settings.
        """
        pass

    @abstractmethod
    def run(self, settings: dict, log_callback) -> bool:
        """
        Método de execução da automação.
        Deve ser thread-safe (executado em thread secundária na UI).

        Parâmetros:
          - settings: Dicionário contendo os valores preenchidos na UI baseados nas especificações.
          - log_callback: Função callback no formato `log_callback(message: str)` para logs em tempo real.

        Retorna:
          - True se concluído com sucesso.
          - False em caso de falha.
        """
        pass
