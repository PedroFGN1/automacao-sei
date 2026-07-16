import os
import sys
import importlib
import traceback
from typing import Dict, List, Type
from src.core.plugin_base import BasePlugin

class PluginManager:
    """
    Responsável por escanear o diretório de plugins, importar os módulos
    dinamicamente e instanciar as subclasses de BasePlugin.
    """
    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            # Caminho padrão: src/plugins/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.plugins_dir = os.path.join(base_dir, "plugins")
        else:
            self.plugins_dir = os.path.abspath(plugins_dir)
            
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_errors: Dict[str, str] = {}

    def load_plugins(self) -> Dict[str, BasePlugin]:
        """
        Escaneia o diretório de plugins e carrega todas as classes válidas que
        herdam de BasePlugin.
        """
        self.plugins.clear()
        self.load_errors.clear()

        if not os.path.exists(self.plugins_dir):
            print(f"[*] Diretório de plugins não encontrado: {self.plugins_dir}")
            return self.plugins

        # Adiciona a pasta de plugins ao sys.path para importação dinâmica correta
        # de forma que possamos importar como 'src.plugins.modulo' ou 'plugins.modulo'
        parent_dir = os.path.dirname(self.plugins_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_") and not filename.startswith("."):
                module_name = filename[:-3]
                try:
                    # Tenta importar o módulo dinamicamente
                    # Prefere importá-lo relativo a 'plugins' ou 'src.plugins'
                    try:
                        module = importlib.import_module(f"src.plugins.{module_name}")
                    except ImportError:
                        module = importlib.import_module(module_name)
                    
                    # Procura classes no módulo que herdem de BasePlugin
                    found_plugin_class = False
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr is not BasePlugin):
                            
                            # Instancia o plugin
                            plugin_instance = attr()
                            plugin_id = plugin_instance.id
                            
                            if plugin_id in self.plugins:
                                print(f"[!] Aviso: Plugin com ID '{plugin_id}' duplicado. Ignorando classe '{attr_name}'.")
                                continue
                                
                            self.plugins[plugin_id] = plugin_instance
                            found_plugin_class = True
                            
                    if not found_plugin_class:
                        print(f"[*] Aviso: Nenhum plugin válido (herdando de BasePlugin) foi encontrado no arquivo {filename}.")
                        
                except Exception as e:
                    error_msg = f"Erro ao carregar o plugin '{module_name}': {str(e)}\n{traceback.format_exc()}"
                    print(f"[!] {error_msg}")
                    self.load_errors[module_name] = error_msg

        return self.plugins

    def get_plugin(self, plugin_id: str) -> BasePlugin:
        """Retorna o plugin instanciado correspondente ao ID fornecido."""
        return self.plugins.get(plugin_id)

    def list_plugins(self) -> List[BasePlugin]:
        """Retorna a lista de todos os plugins carregados com sucesso."""
        return list(self.plugins.values())
