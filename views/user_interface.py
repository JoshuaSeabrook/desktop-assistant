from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QPushButton, \
    QHBoxLayout, QListWidget, QListWidgetItem

from enums import *
from views.chat_bubble import ChatBubble
from views.text_input import TextInput


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.previous_sender = Sender.USER

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WA_TranslucentBackground)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.chatDisplay = QListWidget()
        self.chatDisplay.setAttribute(Qt.WA_TranslucentBackground)
        self.layout.addWidget(self.chatDisplay)

        self.inputLayout = QHBoxLayout()
        self.userInput = TextInput()
        self.userInput.setPlaceholderText("Message assistant...")
        self.userInput.returnPressed.connect(self.send_message)
        self.inputLayout.addWidget(self.userInput)

        self.chatButton = QPushButton(";)")
        button_size = 30  # Set both width and height to this value to get a square
        self.chatButton.setFixedSize(button_size, button_size)  # Use setFixedSize to ensure the button remains square

        self.inputLayout.addWidget(self.chatButton, 0, Qt.AlignRight)
        self.layout.addLayout(self.inputLayout)
        self.centralWidget.setLayout(self.layout)

        self.chatButton.clicked.connect(self.toggle_input_window)
        self.userInput.setVisible(False)  # userInput should start hidden
        self.position_window()

        # Styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: transparent;  
            }}
            QLineEdit {{
                background-color: #333333;
                color: white;
                border: 1px solid #808080;
                border-radius: 10px;
                padding: 5px;
            }}
            QListWidget {{
                background-color: transparent;  
                border: none;  
            }}
            QPushButton {{
                border-radius: {button_size / 2}px;
                background-color: #873f9d;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #9e5fb7;
            }}
            QListWidget::item:selected, QListWidget::item:hover {{
                background-color: transparent;
            }}
        """)

    def position_window(self):
        # Positions and resizes the window. Currently set to 600px width and full height,
        # on the right side of the screen.
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()

        window_width = 600
        window_height = QApplication.desktop().availableGeometry(self).bottom() - 50
        self.setFixedSize(window_width, window_height)

        x = screen_width - window_width
        y = QApplication.desktop().availableGeometry(self).bottom() - window_height

        self.move(x, y)

    def toggle_input_window(self):
        # Toggle the visibility of the userInput widget
        self.userInput.setFocus()
        self.userInput.setVisible(not self.userInput.isVisible())

    def send_message(self):
        user_text = self.userInput.text().strip()
        if user_text:  # Ensure input is not just whitespace
            self.controller.process_input(user_text)
            self.userInput.clear()

    def display_message(self, message, sender=Sender.ASSISTANT):
        # If the sender has changed, add a spacer item before the regular chat bubble
        if self.previous_sender != sender:
            spacer_item = QListWidgetItem(self.chatDisplay)
            spacer_item.setSizeHint(QSize(0, 10))
            self.chatDisplay.addItem(spacer_item)

            # Remove the spacer item after a delay
            spacer_timer = QTimer(self)
            spacer_timer.setSingleShot(True)
            spacer_timer.timeout.connect(lambda: self.remove_message(spacer_item))
            spacer_timer.start(11000)

            # Update previous_sender
            self.previous_sender = sender

        chat_bubble = ChatBubble(message, sender)
        item = QListWidgetItem(self.chatDisplay)
        item.setSizeHint(chat_bubble.sizeHint())
        chat_bubble.fadeOutFinished.connect(lambda: self.remove_message(item))
        self.chatDisplay.addItem(item)
        self.chatDisplay.setItemWidget(item, chat_bubble)

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: chat_bubble.fade_out())
        timer.start(10000)

    def remove_message(self, item):
        index = self.chatDisplay.row(item)
        if index != -1:
            self.chatDisplay.takeItem(index)
