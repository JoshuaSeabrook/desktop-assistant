from models.response_generator import ResponseGenerator
from views.user_interface import UserInterface

class ApplicationController:
    def __init__(self):
        self.model = ResponseGenerator()
        self.view = UserInterface()

    def process_input(self, user_input):
        response = self.model.get_response(user_input)
        self.view.display_message(response)

    def run(self):
        while True:
            user_input = self.view.get_user_input()
            if user_input.lower() == 'exit':
                break
            self.process_input(user_input)