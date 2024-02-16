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
        self.userInput.returnPressed.connect(self.send_message)
        self.inputLayout.addWidget(self.userInput)

        self.chatButton = QPushButton("Chat")
        self.chatButton.setFixedWidth(50)

        self.inputLayout.addWidget(self.chatButton, 0, Qt.AlignRight)
        self.layout.addLayout(self.inputLayout)
        self.centralWidget.setLayout(self.layout)

        self.chatButton.clicked.connect(self.toggle_input_window)
        self.position_window()

        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;  
            }
            QLineEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #808080;
                border-radius: 10px;
                padding: 5px;
            }
            QListWidget {
                background-color: transparent;  
                border: none;  
            }
            QPushButton {
                background-color: #873f9d;
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
        SCREEN_PERCENTAGE = 0.7  # Percentage of the screen height to use
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()

        window_width = 600
        window_height = int(screen.height() * SCREEN_PERCENTAGE)
        self.setFixedSize(window_width, window_height)

        x = screen_width - window_width
        y = int(screen.height() * (1 - SCREEN_PERCENTAGE) / 2)

        self.move(x, y)

    def toggle_input_window(self):
        # Toggle the visibility of the userInput widget
        self.userInput.setVisible(not self.userInput.isVisible())

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
