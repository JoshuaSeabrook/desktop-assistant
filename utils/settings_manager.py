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
        if self.filepath.is_file():
            with open(self.filepath, 'r') as file:
                return json.load(file)
        else:
            print(f"Settings file not found at '{self.filepath}'. Using default settings.")
            return {}

    def save_settings(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()
