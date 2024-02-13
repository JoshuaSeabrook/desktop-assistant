import sys

from PyQt5.QtWidgets import QApplication

from models.response_generator import ResponseGenerator
from views.user_interface import MainWindow


class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = ResponseGenerator()
        self.view = MainWindow(self)

    def process_input(self, user_input):
        self.view.display_message(f"You: {user_input}")
        response = self.model.get_response(user_input)
        self.view.display_message(f"Assistant: {response}")

    def run(self):
        self.view.show()
        sys.exit(self.app.exec_())
