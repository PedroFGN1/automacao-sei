import os
from dotenv import load_dotenv

# Carrega as configurações de ambiente do arquivo .env
load_dotenv()

# Importa o inicializador do banco para garantir que as tabelas SQLite existam
import core.database

# Importa e executa a interface gráfica
from ui.app import App

if __name__ == "__main__":
    print("Iniciando o Gerenciador de Automações SEI Modular...")
    app = App()
    app.mainloop()
