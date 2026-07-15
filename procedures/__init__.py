import os
import pkgutil
import importlib
import inspect
from core.base_procedure import BaseProcedure

# Dicionário global para guardar os procedimentos descobertos: { "NomeDaClasse": Classe }
PROCEDURES = {}

def carregar_procedimentos_dinamicamente():
    """
    Varre dinamicamente a pasta 'procedures' por arquivos Python,
    importa os módulos e descobre classes que estendem 'BaseProcedure'.
    """
    global PROCEDURES
    PROCEDURES.clear()
    
    # Obtém o caminho da pasta procedures
    pkg_dir = os.path.dirname(__file__)
    pkg_name = __name__
    
    for _, module_name, is_pkg in pkgutil.iter_modules([pkg_dir]):
        if is_pkg:
            continue
        try:
            # Importa o módulo dinamicamente
            modulo = importlib.import_module(f"{pkg_name}.{module_name}")
            
            # Varre os membros do módulo em busca de classes
            for name, obj in inspect.getmembers(modulo, inspect.isclass):
                # Verifica se é subclasse de BaseProcedure e não a própria classe base
                if issubclass(obj, BaseProcedure) and obj is not BaseProcedure:
                    PROCEDURES[name] = obj
        except Exception as exc:
            print(f"Erro ao carregar módulo de automação {module_name}: {exc}")

# Executa a descoberta de procedimentos na inicialização do pacote
carregar_procedimentos_dinamicamente()
