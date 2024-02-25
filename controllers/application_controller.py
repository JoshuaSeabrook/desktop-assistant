import sys

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, QMetaObject, Q_ARG
from PyQt5.QtWidgets import QApplication

from enums import *
from models.response_generator import ResponseGenerator
from views.user_interface import MainWindow


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

        self.thread = QThread()
        self.inputProcessor = InputProcessor(self.model)
        self.inputProcessor.moveToThread(self.thread)
        self.inputProcessor.finished.connect(self.update_ui_with_response)
        self.thread.start()

    def process_input(self, user_input):
        self.view.userInput.returnPressed.disconnect(self.view.send_message)
        self.view.display_message(user_input, Sender.USER)
        QMetaObject.invokeMethod(self.inputProcessor, 'process', Q_ARG(str, user_input))

    def update_ui_with_response(self, response):
        self.view.display_message(response)
        self.view.userInput.returnPressed.connect(self.view.send_message)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec_())
