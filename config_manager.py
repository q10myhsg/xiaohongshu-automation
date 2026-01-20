# Configuration Manager

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from the config file."""
        import json
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def get(self, key):
        """Retrieve a value from the configuration by key."""
        return self.config.get(key)

    def set(self, key, value):
        """Set a value in the configuration by key."""
        self.config[key] = value
        self.save_config()

    def save_config(self):
        """Save the configuration back to the file."""
        import json
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def reload(self):
        """Reload the configuration from the file."""
        self.config = self.load_config()