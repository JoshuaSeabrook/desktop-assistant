from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QPushButton, \
    QHBoxLayout, QListWidget, QListWidgetItem

from enums import *
from views.chat_bubble import ChatBubble


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WA_TranslucentBackground)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.chatDisplay = QListWidget()
        self.chatDisplay.setAttribute(Qt.WA_TranslucentBackground)
        self.layout.addWidget(self.chatDisplay)

        self.inputLayout = QHBoxLayout()
        self.userInput = QLineEdit()
        self.userInput.setPlaceholderText("Message assistant...")
        self.inputLayout.addWidget(self.userInput)

        self.sendButton = QPushButton("Send")
        self.inputLayout.addWidget(self.sendButton)
        self.layout.addLayout(self.inputLayout)
        self.centralWidget.setLayout(self.layout)

        self.sendButton.clicked.connect(self.send_message)
        self.position_window()

        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;  
            }
            QListWidget {
                background-color: transparent;  
                border: none;  
            }
            QLineEdit {
                border: 1px solid #dcdcdc;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 5px;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QListWidget::item:selected, QListWidget::item:hover {
                background-color: transparent;
            }
        """)

    def position_window(self):
        # Positions and resizes the window. Currently set to 600px width and full height,
        # on the right side of the screen.
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()

        window_width = 600
        window_height = screen.height()
        self.setFixedSize(window_width, window_height)

        x = screen_width - window_width
        y = 0

        self.move(x, y)

    def send_message(self):
        user_text = self.userInput.text().strip()
        if user_text:  # Ensure input is not just whitespace
            self.controller.process_input(user_text)
            self.userInput.clear()

    def display_message(self, message, sender=Sender.ASSISTANT):
        chat_bubble = ChatBubble(message, sender)
        item = QListWidgetItem(self.chatDisplay)
        item.setSizeHint(chat_bubble.sizeHint())
        self.chatDisplay.addItem(item)
        self.chatDisplay.setItemWidget(item, chat_bubble)
