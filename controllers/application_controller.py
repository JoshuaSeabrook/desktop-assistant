import json
import sys

from PyQt5.QtCore import QThread, QMetaObject, Q_ARG, QTimer, Qt
from PyQt5.QtWidgets import QApplication

from enums import *
from models.assistant_mind import AssistantMind
from models.response_generator import ResponseGenerator
from utils import font_manager
from utils.settings_manager import SettingsManager
from views.user_interface import MainWindow
from models.speech_generator import SpeechGenerator
from models.transciber import Transcriber
from integrations.gmail import GmailClient
from integrations.webpage_handler import WebpageHandler
from integrations.file_handler import FileHandler


class ApplicationController:
    def __init__(self):
        self.is_return_pressed_connected = True
        self.app = QApplication(sys.argv)

        self.view = MainWindow(self)
        self.transcriber = Transcriber()
        self.is_return_pressed_connected = True

        self.settings_manager = SettingsManager()

        self.sentences = []
        self.functions = self.init_functions()

        self.model = ResponseGenerator(functions=self.functions)

        # Thread creation

        self.speech_thread = QThread()
        self.speech_generator = SpeechGenerator()
        self.speech_generator.moveToThread(self.speech_thread)
        self.speech_generator.finished.connect(self.display_message)
        self.speech_generator.start_speaking.connect(self.started_speaking)
        self.speech_generator.finished_speaking.connect(self.finished_speaking)
        self.speech_generator.finished_speaking.connect(self.enable_input)
        self.speech_thread.start()

        self.input_thread = QThread()
        self.model.moveToThread(self.input_thread)
        self.model.new_data_signal.connect(self.process_audio)
        self.model.start_generating_signal.connect(self.disable_input)
        self.model.function_call.connect(self.process_function_call)
        self.input_thread.start()

        self.brain_thread = QThread()
        self.assistantMind = AssistantMind()
        self.assistantMind.moveToThread(self.brain_thread)
        self.assistantMind.requestMessage.connect(self.generate_message)
        self.brain_thread.start()

        self.transcriber_thread = QThread()
        self.transcriber = Transcriber()
        self.transcriber.moveToThread(self.transcriber_thread)
        self.transcriber.transcription_complete.connect(self.process_input)
        self.transcriber_thread.start()

        self.gmail_client = GmailClient()

        self.webpage_fetcher = WebpageHandler()

        self.file_handler = FileHandler()

        QMetaObject.invokeMethod(self.assistantMind, 'start', Qt.AutoConnection)

    def disable_text_input(self, disconnect=True):
        """Manages the connection state of the returnPressed signal."""
        if disconnect and self.is_return_pressed_connected:
            # Disconnect only if it's currently connected
            self.view.userInput.returnPressed.disconnect(self.view.send_message)
            self.view.assistant_icon.animate_in()
            self.is_return_pressed_connected = False
            return True
        elif not disconnect and not self.is_return_pressed_connected:
            # Reconnect only if it's currently disconnected
            self.view.userInput.returnPressed.connect(self.view.send_message)
            self.view.assistant_icon.animate_out()
            self.is_return_pressed_connected = True
            return True
        return False

    def disable_input(self):
        """Called when response generation is started, disables input while generation is in progress"""
        self.disable_text_input(True)

    def finished_speaking(self):
        """Called when audio playback is finished, stops the pulse animation of the assistant icon."""
        self.view.assistant_icon.stop_pulse_animation()

    def started_speaking(self):
        """Called when audio playback is started, starts the pulse animation of the assistant icon."""
        self.view.assistant_icon.start_pulse_animation()

    def enable_input(self):
        """Called when response generation is finished, waits for speech generation to finish before enabling input"""
        if self.speech_generator.is_playing_audio or self.speech_generator.sentence_queue or self.speech_generator.audio_queue:
            QTimer.singleShot(500, self.enable_input)
        else:
            self.disable_text_input(False)
            QMetaObject.invokeMethod(self.assistantMind, 'input_enabled_event', Qt.AutoConnection)

    def generate_message(self, prompt):
        """Generate a message based on a system prompt"""
        # If input is already disabled, generation is currently in progress, therefore return
        if not self.disable_text_input(True):
            return

        QMetaObject.invokeMethod(self.model, 'get_response', Q_ARG(str, prompt), Q_ARG(Role, Role.SYSTEM))

    def process_input(self, user_input, display_message=False):
        """Display the user's input and send it to the ResponseGenerator."""
        self.disable_text_input(True)
        if display_message:
            self.view.display_message(user_input, Sender.USER)
        QMetaObject.invokeMethod(self.model, 'get_response', Q_ARG(str, user_input), Q_ARG(Role, Role.USER))

    def process_audio_input(self):
        """Start transcribing audio from the microphone."""
        if not self.disable_text_input(True):
            return

        QMetaObject.invokeMethod(self.transcriber, 'transcribe_from_microphone')
        self.disable_text_input(True)

    def display_message(self):
        """Display the next sentence in the conversation.
        This method is connected to the finished signal from the SpeechGenerator."""
        self.view.assistant_icon.start_pulse_animation()
        if self.settings_manager.get_setting("assistant_chat_bubbles", True):
            self.view.display_message(self.sentences.pop(0))
        else:
            self.sentences.pop(0)

    def process_audio(self, response):
        """Process the response from the ResponseGenerator and send it to the SpeechGenerator."""
        self.sentences.append(response)
        QMetaObject.invokeMethod(self.speech_generator, 'add_sentence',
                                 Qt.QueuedConnection, Q_ARG(str, response))

    def cleanup(self):
        """Clean up threads when the application is closed."""
        self.input_thread.quit()
        self.input_thread.wait()
        self.speech_thread.quit()
        self.speech_thread.wait()

    def run(self):
        """Run the application."""
        self.app.aboutToQuit.connect(self.cleanup)
        font_manager.load_application_fonts(self.app)
        self.view.show()
        sys.exit(self.app.exec_())

    # =================
    # Function handling
    # =================

    def init_functions(self):
        """Initialize the functions that the assistant can perform."""
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "continuous_responses",
                    "description": "Enables or disables continuous responses - enabling you to continue generating responses at the specified interval",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "enabled": {
                                "type": "boolean",
                                "description": "Whether to continuously respond to the user."
                            },
                            "frequency": {
                                "type": "integer",
                                "description": "The frequency to respond to the user, in seconds."
                            }
                        },
                        "required": ["enabled"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_emails",
                    "description": "Returns recent emails from the user's inbox.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quantity": {
                                "type": "integer",
                                "description": "The number of emails to return"
                            },
                        },
                        "required": ["quantity"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Sends an email on the users behalf.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "The email address of the recipient"
                            },
                            "subject": {
                                "type": "string",
                                "description": "The subject line of the email"
                            },
                            "body": {
                                "type": "string",
                                "description": "The content of the email"
                            },
                        },
                        "required": ["to", "subject", "body"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_webpage_content",
                    "description": "Returns the content of a webpage. If the user requests a google search, use duckduckgo instead. This should be called if you want to get information from a webpage.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the webpage"
                            },
                        },
                        "required": ["url"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_webpage",
                    "description": "Opens a webpage in the users default browser. This should be called if the user wants to see a webpage.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the webpage"
                            },
                        },
                        "required": ["url"]
                    },
                }
            }
            ,
            {
                "type": "function",
                "function": {
                    "name": "open_file",
                    "description": "Opens a file in the default application.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path of the file"
                            },
                        },
                        "required": ["file_path"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_files_in_directory",
                    "description": "Returns a list of files and dirs in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dir_path": {
                                "type": "string",
                                "description": "The path of the directory"
                            },
                        },
                        "required": ["file_path"]
                    },
                }
            }
        ]
        return functions

    def process_function_call(self, function_call, arg_string):
        """Process a function call from the ResponseGenerator."""
        try:
            arguments = json.loads(arg_string)
            return_string = ""
            match function_call:
                case "continuous_responses":  # Enables or disables continuous responses
                    if arguments["enabled"]:
                        QMetaObject.invokeMethod(self.assistantMind, 'set_continuous_responses'
                                                 , Q_ARG(bool, arguments["enabled"]),
                                                 Q_ARG(int, arguments["frequency"]))
                        return_string = "Continuous responses " + (
                            "enabled" if arguments["enabled"] else "disabled") + " at a frequency of " + str(
                            arguments["frequency"]) + " seconds."
                    else:
                        QMetaObject.invokeMethod(self.assistantMind, 'set_continuous_responses'
                                                 , Q_ARG(bool, arguments["enabled"]), Q_ARG(int, 0))
                        return_string = "Continuous responses disabled."
                case "get_emails":  # Returns the result of the read_emails function
                    return_string = str(self.gmail_client.read_emails(max_results=arguments["quantity"]))
                case "send_email":  # Sends an email
                    self.gmail_client.send_email(arguments["to"], arguments["subject"], arguments["body"])
                    return_string = "Email sent successfully."
                case "get_webpage_content":  # Returns the content of a webpage
                    return_string = self.webpage_fetcher.get_content(arguments["url"])
                case "open_webpage":  # Opens a webpage in the default browser
                    self.webpage_fetcher.open_link(arguments["url"])
                    return_string = "Webpage opened successfully."
                case "open_file":  # Opens a file using the default program
                    return_string = self.file_handler.open_file_with_default_program(arguments["file_path"])
                case "get_files_in_directory":  # Returns a list of files and directories in a directory
                    return_string = str(self.file_handler.get_files_in_directory(arguments["dir_path"]))
        except Exception as e:
            return_string = str(e)
        # Return the result of the function call to the ResponseGenerator
        QMetaObject.invokeMethod(self.model, 'function_return', Q_ARG(str, return_string))
