import threading
import queue
import time
from typing import Dict, Any, Callable
from app.core.plugin_base import BasePlugin

class PluginExecutor:
    """
    Executa a lógica do plugin de automação em uma thread separada,
    capturando logs e exceções de forma thread-safe.
    """
    def __init__(self, plugin: BasePlugin, params: Dict[str, Any]):
        self.plugin = plugin
        self.params = params
        self.log_queue = queue.Queue()
        self.thread = None
        self.is_running = False
        self.result = None
        self.error = None

    def start(self, on_finish: Callable[[Dict[str, Any], Exception], None] = None):
        """
        Inicia a execução do plugin em uma thread separada (daemon).
        """
        self.is_running = True
        self.result = None
        self.error = None
        
        self.thread = threading.Thread(
            target=self._run_wrapper, 
            args=(on_finish,),
            daemon=True
        )
        self.thread.start()

    def _run_wrapper(self, on_finish: Callable[[Dict[str, Any], Exception], None]):
        """
        Wrapper executado na thread secundária que encapsula a chamada
        do plugin e captura logs e erros.
        """
        def logger_callback(message: str, level: str = "INFO"):
            # Enfileira tupla (timestamp, level, message)
            self.log_queue.put((time.time(), level, message))

        try:
            logger_callback(f"Iniciando execução do plugin '{self.plugin.name}'...", "INFO")
            # Executa o plugin
            self.result = self.plugin.execute(self.params, logger_callback)
            logger_callback("Execução do plugin concluída com sucesso.", "INFO")
        except Exception as e:
            self.error = e
            logger_callback(f"Erro fatal durante a execução: {str(e)}", "ERROR")
        finally:
            self.is_running = False
            if on_finish:
                try:
                    on_finish(self.result, self.error)
                except Exception as callback_err:
                    # Loga erro interno do callback apenas no terminal de depuração
                    print(f"[!] Erro no callback de término: {str(callback_err)}")

    def get_logs(self) -> list:
        """
        Extrai todos os logs pendentes da fila com segurança para serem lidos
        pela thread principal do Tkinter.
        """
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs
