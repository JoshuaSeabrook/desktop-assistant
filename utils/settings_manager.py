import json
from pathlib import Path


class SettingsManager:
    _instance = None

    def __new__(cls, filepath="config/settings.json"):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance.filepath = Path(filepath)
            cls._instance.settings = cls._instance.load_settings()
        return cls._instance

    def load_settings(self):
        """Loads the settings from the settings file."""
        if self.filepath.is_file():
            with open(self.filepath, 'r') as file:
                return json.load(file)
        else:
            print(f"Settings file not found at '{self.filepath}'. Using default settings.")
            return {}

    def save_settings(self):
        """Saves the settings to the settings file."""
        with open(self.filepath, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get_setting(self, key, default=None):
        """Returns the value of a setting given its key, or a default value if the key is not found."""
        return self.settings.get(key, default)

    def update_setting(self, key, value):
        """Updates the value of a setting given its key. If the key does not exist, it is created."""
        self.settings[key] = value
        self.save_settings()
