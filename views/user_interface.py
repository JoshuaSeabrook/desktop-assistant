from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QTextEdit, QLineEdit, QPushButton, QApplication

class MainWindow(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Desktop Assistant")
        self.setGeometry(100, 100, 600, 400)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.chatDisplay = QTextEdit()
        self.chatDisplay.setReadOnly(True)
        self.layout.addWidget(self.chatDisplay)

        self.userInput = QLineEdit()
        self.userInput.setPlaceholderText("Type your message here...")
        self.layout.addWidget(self.userInput)

        self.sendButton = QPushButton("Send")
        self.layout.addWidget(self.sendButton)

        self.centralWidget.setLayout(self.layout)

        self.sendButton.clicked.connect(self.send_message)

    def send_message(self):
        user_text = self.userInput.text().strip()
        if user_text:  # Ensure input is not just whitespace
            self.controller.process_input(user_text)
            self.userInput.clear()

    def display_message(self, message):
        self.chatDisplay.append(message)
