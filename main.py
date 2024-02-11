from controllers.application_controller import ApplicationController

if __name__ == '__main__':
    controller = ApplicationController()
    while True:
        user_input = controller.view.get_user_input()
        if user_input.lower() == 'exit':
            break
        controller.process_input(user_input)
