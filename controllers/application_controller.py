import sys
import re

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, QMetaObject, Q_ARG, QTimer, Qt
from PyQt5.QtWidgets import QApplication

from enums import *
from models.response_generator import ResponseGenerator
from views.user_interface import MainWindow
from models.speech_generator import SpeechGenerator


class InputProcessor(QObject):
    finished = pyqtSignal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model

    @pyqtSlot(str)
    def process(self, user_input):
        response = self.model.get_response(user_input)
        self.finished.emit(response)


class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = ResponseGenerator()
        self.view = MainWindow(self)

        self.sentences = []

        # Thread creation

        self.speech_thread = QThread()
        self.speech_generator = SpeechGenerator()
        self.speech_generator.moveToThread(self.speech_thread)
        self.speech_generator.finished.connect(self.display_message)
        self.speech_thread.start()

        self.input_thread = QThread()
        self.inputProcessor = InputProcessor(self.model)
        self.inputProcessor.moveToThread(self.input_thread)
        self.inputProcessor.finished.connect(self.process_audio)
        self.input_thread.start()

    def process_input(self, user_input):
        self.view.userInput.returnPressed.disconnect(self.view.send_message)
        self.view.display_message(user_input, Sender.USER)
        QMetaObject.invokeMethod(self.inputProcessor, 'process', Q_ARG(str, user_input))

    def display_message(self):
        """Display the next sentence in the conversation.
        This method is connected to the finished signal from the SpeechGenerator."""
        self.view.display_message(self.sentences.pop(0))
        if len(self.sentences) == 0:
            self.view.userInput.returnPressed.connect(self.view.send_message)

    def process_audio(self, response):
        """Process the response from the ResponseGenerator and send it to the SpeechGenerator."""
        # Use regex to split the response into sentences without removing punctuation
        self.sentences = re.split('(?<=[.!?])\s+', response.strip())

        # Add each sentence to speech generator
        for sentence in self.sentences:
            QMetaObject.invokeMethod(self.speech_generator, 'add_sentence',
                                     Qt.QueuedConnection, Q_ARG(str, sentence))

        if not self.sentences:  # In case of empty response, the user can still type in a new message
            self.view.userInput.returnPressed.connect(self.view.send_message)
        else:
            # The SpeechGenerator will play the sentences in the queue until empty
            QMetaObject.invokeMethod(self.speech_generator, 'play_next_audio',
                                     Qt.QueuedConnection)

    def cleanup(self):
        """Clean up threads when the application is closed."""
        self.input_thread.quit()
        self.input_thread.wait()
        self.speech_thread.quit()
        self.speech_thread.wait()

    def run(self):
        self.app.aboutToQuit.connect(self.cleanup)
        self.view.show()
        sys.exit(self.app.exec_())
