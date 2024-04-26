import re

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QEventLoop
from openai import OpenAI

from enums import Role
from utils.settings_manager import SettingsManager


class ResponseGenerator(QObject):
    new_data_signal = pyqtSignal(str)
    start_generating_signal = pyqtSignal()
    finished_generating_signal = pyqtSignal()
    function_call = pyqtSignal(str, str)
    function_call_completed = pyqtSignal()

    def __init__(self, model: str = "gpt-4-turbo", functions=None):
        super().__init__()

        self.model = model
        self.settings_manager = SettingsManager()
        self.called_function = None
        self.client = OpenAI(api_key=self.settings_manager.get_setting("api_key"))
        self.sentence_buffer = ""
        self.full_response = ""  # Initialize a variable to accumulate the full response
        system_message = self.settings_manager.get_setting("assistant_personality", "You are a desktop assistant.")  # Loads the assistant's personality
        external_apps = str(self.settings_manager.get_setting("external_applications", []))  # Loads any custom external apps to be passed to the assistant
        user_info = self.settings_manager.get_setting("user_info", "You have no details on the user.")  # Loads any user info to be passed to the assistant
        self.message_history = [{"role": "system", "content": system_message + "\nExternal Apps: " + external_apps + "\nUser Info: " + user_info}, {"role": "user", "content": "Hello"}]  # Construct the initial message history
        if functions:
            self.tools = functions


    @pyqtSlot(str, Role)
    def get_response(self, user_input: str = None, message_role: Role = Role.USER):
        """Generates a response to the user's input. If no input is provided, the assistant will generate a response based on the message history."""
        self.start_generating_signal.emit()
        try:
            if user_input:
                self.message_history.append({"role": message_role.name.lower(), "content": user_input})
            response_object = self.client.chat.completions.create(
                model=self.model,
                messages=self.message_history,
                temperature=0,
                stream=True,
                tools=self.tools
            )

            for chunk in response_object:
                if hasattr(chunk.choices[0].delta, 'tool_calls'):
                    if chunk.choices[0].delta.tool_calls:
                        # For some reason function calls do not work with streaming, so we have to handle them separately
                        function_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=self.message_history,
                            temperature=0,
                            stream=False,
                            tools=self.tools
                        )
                        self.called_function = function_response.choices[0].message.tool_calls[0]
                        self.message_history.append(
                            {"role": "assistant", "content": None, "tool_calls": function_response.choices[0].message.tool_calls})
                        self.execute_function_call(function_response.choices[0].message)
                        self.get_response()
                        return
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        self.full_response += content
                        self.sentence_buffer += content
                        self.emit_complete_sentences()
                    elif content is None:
                        self.handle_end_of_message()
                        break

            if self.sentence_buffer.strip():
                self.new_data_signal.emit(self.sentence_buffer.strip())
                self.sentence_buffer = ""


        except Exception as e:
            print(f"Error in streaming response: {e}")
            self.new_data_signal.emit("Sorry, I encountered an error.")

        self.finished_generating_signal.emit()

    def handle_end_of_message(self):
        """Handles the end of a message by emitting the full response and clearing the sentence buffer."""
        self.message_history.append({"role": "assistant", "content": self.full_response})

        self.full_response = ""
        if self.sentence_buffer.strip():
            self.new_data_signal.emit(self.sentence_buffer.strip())
            self.sentence_buffer = ""

    def emit_complete_sentences(self):
        """Checks the buffer for complete sentences and emits them."""
        while True:
            quote_indices = [m.start() for m in re.finditer('"', self.sentence_buffer)]

            if len(quote_indices) >= 2:
                second_quote_index = quote_indices[1]
                quoted_sentence = self.sentence_buffer[:second_quote_index + 1].strip()
                self.sentence_buffer = self.sentence_buffer[second_quote_index + 1:].strip()
                if quoted_sentence:
                    self.new_data_signal.emit(quoted_sentence)
                    continue

            pattern = re.compile(r'(?<=[.!?])\s+')
            match = pattern.search(self.sentence_buffer)
            if match:
                sentence_end = match.start() + 1
                complete_sentence = self.sentence_buffer[:sentence_end].strip()
                quote_indices = [m.start() for m in re.finditer('"', complete_sentence)]
                if complete_sentence and len(quote_indices) == 0:
                    self.sentence_buffer = self.sentence_buffer[sentence_end:].strip()
                    self.new_data_signal.emit(complete_sentence)
                else:
                    break
            else:
                break

    def execute_function_call(self, message):
        """Executes a function call from the assistant."""
        self.function_response = None
        print(message.tool_calls[0].function)
        self.function_call.emit(message.tool_calls[0].function.name, message.tool_calls[0].function.arguments)

        loop = QEventLoop()
        self.function_call_completed.connect(loop.quit) # Loops until the function call is completed

        loop.exec_()

        self.message_history.append({
            "role": "tool",
            "content": self.function_response,
            "tool_call_id": message.tool_calls[0].id
        })

    @pyqtSlot(str)
    def function_return(self, response):
        """Receives the response from a function call."""
        print(f"Function response: {response}")
        self.function_response = response
        self.function_call_completed.emit()