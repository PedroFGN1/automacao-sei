import os
import sys
import unittest

# Adiciona o diretório raiz ao sys.path para execução correta dos testes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.plugin_base import BasePlugin
from app.core.plugin_manager import PluginManager

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        # Localiza o diretório de plugins relativo a este arquivo de teste
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.plugins_dir = os.path.join(base_dir, "plugins")
        self.manager = PluginManager(self.plugins_dir)

    def test_load_plugins(self):
        """Testa se todos os plugins do diretório são importados e carregados corretamente."""
        plugins = self.manager.load_plugins()
        
        # Garante que carregou plugins
        self.assertTrue(len(plugins) > 0, "Nenhum plugin foi carregado pelo PluginManager.")
        
        # Verifica se os plugins core estão na lista
        self.assertIn("dummy_robot", plugins, "Plugin dummy não foi carregado.")
        self.assertIn("enviar_n8n", plugins, "Plugin n8n não foi carregado.")
        self.assertIn("indexador_pdf", plugins, "Plugin indexador não foi carregado.")
        self.assertIn("exportador_sei", plugins, "Plugin exportador do SEI não foi carregado.")

    def test_plugin_properties(self):
        """Testa se cada plugin implementa e retorna os metadados corretos."""
        self.manager.load_plugins()
        
        for plugin_id, plugin in self.manager.plugins.items():
            self.assertIsInstance(plugin, BasePlugin, f"Plugin {plugin_id} não herda de BasePlugin.")
            
            # Valida metadados obrigatórios
            self.assertTrue(len(plugin.id) > 0, f"O plugin {plugin_id} está com ID vazio.")
            self.assertTrue(len(plugin.name) > 0, f"O plugin {plugin_id} está com nome vazio.")
            self.assertTrue(len(plugin.description) > 0, f"O plugin {plugin_id} está com descrição vazia.")
            
            # Valida que get_params_schema retorna uma lista
            schema = plugin.get_params_schema()
            self.assertIsInstance(schema, list, f"O schema do plugin {plugin_id} não é uma lista.")
            
            for param in schema:
                self.assertIn("name", param, f"Parâmetro em {plugin_id} não possui campo 'name'.")
                self.assertIn("label", param, f"Parâmetro em {plugin_id} não possui campo 'label'.")
                self.assertIn("type", param, f"Parâmetro em {plugin_id} não possui campo 'type'.")
                self.assertIn(param["type"], ["text", "password", "file", "directory", "bool"], f"Tipo inválido '{param['type']}' em {plugin_id}.")

    def test_load_errors_is_empty(self):
        """Garante que nenhum erro de importação de sintaxe ocorreu na pasta de plugins."""
        self.manager.load_plugins()
        self.assertEqual(len(self.manager.load_errors), 0, f"Erros ocorridos no carregamento de plugins: {self.manager.load_errors}")

if __name__ == "__main__":
    unittest.main()
