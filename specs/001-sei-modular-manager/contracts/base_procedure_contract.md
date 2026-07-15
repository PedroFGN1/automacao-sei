# Interface Contract: BaseProcedure

**Feature**: [spec.md](file:///C:/Users/pedro.galvao/Documents/automacao-sei/specs/001-sei-modular-manager/spec.md)

Este documento estabelece o contrato técnico (API interna) que todo novo procedimento de automação deve seguir. Ao implementar este contrato, a interface do usuário detectará a automação e renderizará seus campos de configuração automaticamente na UI.

## Definição da Classe Abstrata (`core/base_procedure.py`)

```python
from abc import ABC, abstractmethod

class BaseProcedure(ABC):
    @property
    @abstractmethod
    def fixed_settings(self) -> dict:
        """
        Retorna a especificação das configurações estáticas exigidas pelo procedimento.
        Formato de retorno esperado:
        {
            "CAMPO_ID": {
                "label": "Rótulo de Exibição na UI",
                "type": "string" | "path" | "password",
                "default": "Valor Padrão",
                "description": "Texto descritivo de ajuda"
            }
        }
        """
        pass

    @property
    @abstractmethod
    def variable_settings(self) -> dict:
        """
        Retorna a especificação das configurações de execução dinâmicas exigidas.
        Formato de retorno esperado idêntico ao fixed_settings.
        """
        pass

    @abstractmethod
    def run(self, settings: dict, log_callback) -> bool:
        """
        Método principal de execução da automação.
        Deve ser thread-safe (executado em thread secundária).
        
        Parâmetros:
          - settings: Dicionário contendo os valores preenchidos pelo usuário baseados em
                      fixed_settings e variable_settings.
          - log_callback: Função callback no formato `log_callback(message: str)` para emitir logs.
          
        Retorno:
          - True em caso de sucesso completo.
          - False se a automação falhar em seus objetivos.
        """
        pass
```

## Exemplo de Implementação (`procedures/exportador_sei.py`)

```python
from core.base_procedure import BaseProcedure

class ExportadorSei(BaseProcedure):
    @property
    def fixed_settings(self) -> dict:
        return {
            "sei_url": {
                "label": "URL do SEI",
                "type": "string",
                "default": "https://sei.exemplo.gov.br",
                "description": "URL base do sistema SEI"
            },
            "usuario": {
                "label": "Usuário",
                "type": "string",
                "default": "",
                "description": "Nome de login do usuário"
            }
        }

    @property
    def variable_settings(self) -> dict:
        return {
            "caminho_planilha": {
                "label": "Planilha de Entrada",
                "type": "path",
                "default": "",
                "description": "Caminho do arquivo Excel contendo processos a exportar"
            }
        }

    def run(self, settings: dict, log_callback) -> bool:
        log_callback("Iniciando o procedimento de exportação do SEI...")
        # Lógica de automação usando Playwright ou outras ferramentas
        sei_url = settings.get("sei_url")
        log_callback(f"Conectando ao SEI: {sei_url}")
        
        # Simulação de sucesso
        log_callback("Procedimento finalizado com sucesso.")
        return True
```
