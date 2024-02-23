from openai import OpenAI

from utils.settings_manager import SettingsManager


class ResponseGenerator:
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI()
        self.model = model
        self.settings_manager = SettingsManager()
        system_message = self.settings_manager.get_setting("system_message", "You are a desktop assistant.")
        self.message_history = [{"role": "system", "content": system_message}]

    def get_response(self, user_input: str) -> str:
        try:
            self.message_history.append({"role": "user", "content": user_input})
            response_object = self.client.chat.completions.create(
                model=self.model,
                messages=self.message_history
            )
            response_string = str(response_object.choices[0].message.content or "EMPTY STRING")
            self.message_history.append({"role": "assistant", "content": response_string})
            return response_string
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error."
