import importlib
import os
import sys

#Global plugin registry
PLUGIN_REGISTRY = {}

def register_plugin(name, plugin_class):
    PLUGIN_REGISTRY[name] = plugin_class
    print(f"Registered plugin: {name}")

def load_plugins():
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    sys.path.append(plugin_dir)

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"{__package__}.plugins.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                print(f"Skipped plugin '{filename}': Missing dependency - {e}")
            except Exception as e:
                print(f"Failed to load plugin '{filename}': {e}")

def get_plugins():
    return PLUGIN_REGISTRY