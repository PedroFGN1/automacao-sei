# Plugin Interface Contract

Este contrato define a interface abstrata e a estrutura que todo plugin deve implementar para ser detectado pelo `PluginManager` e renderizado pelo formulário dinâmico da interface Tkinter.

## 1. Estrutura do Arquivo de Plugin

Cada plugin deve ser colocado na pasta `src/plugins/` (ou caminho correspondente) e conter uma classe que herde da classe abstrata `BasePlugin` e que use um nome terminando com `Plugin` (ex: `class ExportadorSeiPlugin(BasePlugin)`).

## 2. A Classe Abstrata Base (`BasePlugin`)

Abaixo está o contrato da classe Python base (pseudocódigo da interface obrigatória):

```python
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
            params: Dicionário contendo os valores preenchidos na interface
                    (chaves mapeadas pelo 'name' do schema de parâmetros).
            logger: Função callback para registrar logs em tempo real na UI.
                    Assinatura: logger(mensagem: str, nivel: str) onde nivel é 'INFO', 'WARNING' ou 'ERROR'.
                    
        Returns:
            Dicionário com o resultado final da execução (ex: status, total de itens processados,
            lista de arquivos exportados com sucesso).
            
        Raises:
            Exception: Qualquer exceção não capturada será tratada como erro fatal e
                       reportada como falha na UI.
        """
        pass
```

## 3. Fluxo de Execução e Ciclo de Vida do Plugin

1. **Descoberta**: O `PluginManager` importa todos os módulos da pasta de plugins. Identifica as classes que herdam de `BasePlugin` e as instancia.
2. **Registro**: A UI solicita os metadados do plugin (`id`, `name`, `description`) e preenche o Combobox de seleção.
3. **Formulário**: Ao selecionar um plugin, a UI limpa o painel de parâmetros, lê `get_params_schema()` e desenha os componentes Tkinter correspondentes.
4. **Validação**: Quando o usuário clica em "Iniciar", a UI valida se todos os parâmetros marcados com `is_required: True` possuem valor.
5. **Iniciação**: O sistema cria uma thread de background, desabilita a UI e invoca `plugin.execute(params, ui_logger)`.
6. **Finalização**: O método retorna ou lança uma exceção. A UI reabilita os controles, apresenta pop-ups baseados no sucesso/erro e atualiza o histórico.
