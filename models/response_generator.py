from openai import OpenAI


class ResponseGenerator:
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI()
        self.model = model
        self.message_history = [{"role": "system", "content": "You are a desktop assistant."}]

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
