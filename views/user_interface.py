import winsound
from PyQt5.QtCore import Qt, QTimer, QSize, Q_ARG
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QPushButton, \
    QHBoxLayout, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy

from enums import *
from utils.settings_manager import SettingsManager
from views.assistant_icon import AssistantIcon
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

        self.assistant_icon = AssistantIcon(self)
        # Add a spacer to push the icon down
        spacer = QSpacerItem(20, 55, QSizePolicy.Minimum)
        self.layout.insertSpacerItem(0, spacer)

        self.chatDisplay = QListWidget()
        self.chatDisplay.setAttribute(Qt.WA_TranslucentBackground)
        self.layout.addWidget(self.chatDisplay)

        self.inputLayout = QHBoxLayout()
        self.userInput = TextInput()
        self.userInput.setPlaceholderText("Message assistant...")
        self.userInput.returnPressed.connect(self.send_message)
        self.inputLayout.addWidget(self.userInput)

        self.chatButton = QPushButton(";)")
        button_size = 30
        self.chatButton.setFixedSize(button_size, button_size)

        self.inputLayout.addWidget(self.chatButton, 0, Qt.AlignRight)
        self.layout.addLayout(self.inputLayout)
        self.centralWidget.setLayout(self.layout)

        self.chatButton.clicked.connect(self.toggle_input_window)
        self.position_window()

        # Styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: transparent;  
            }}
            QLineEdit {{
                background-color: rgba(51, 51, 51, 0.9);
                color: white;
                border: 1px solid rgba(128, 128, 128, 0.9);
                border-radius: 3px;
                padding: 5px;
            }}
            QListWidget {{
                background-color: transparent;  
                border: none;  
            }}
            QPushButton {{
                border-radius: 5px;
                background-color: rgba(74, 65, 177, 0.9);
                color: white;
            }}
            QPushButton:hover {{
                background-color: rgba(54, 45, 157, 1.0);
            }}
            QListWidget::item:selected, QListWidget::item:hover {{
                background-color: transparent;
            }}
        """)

    def position_window(self):
        """Positions the window."""
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()

        window_width = 600
        window_height = QApplication.desktop().availableGeometry(self).bottom() - 50
        self.setFixedSize(window_width, window_height)

        x = screen_width - window_width
        y = QApplication.desktop().availableGeometry(self).bottom() - window_height

        self.move(x, y)

    def toggle_input_window(self):
        """Toggle the visibility of the userInput widget, or process audio input if voice input is enabled."""
        if SettingsManager().get_setting("voice_input", True):
            self.controller.process_audio_input()
        else:
            self.userInput.setFocus()
            self.userInput.setVisible(not self.userInput.isVisible())


    def send_message(self):
        """Sends a message to the controller."""
        user_text = self.userInput.text().strip()
        if user_text:  # Ensure input is not just whitespace
            self.controller.process_input(user_text, True)
            self.userInput.clear()

    def display_message(self, message, sender=Sender.ASSISTANT):
        """Displays a message in the chat display."""
        # If the sender has changed, add a spacer item before the regular chat bubble
        if self.previous_sender != sender:
            spacer_item = QListWidgetItem(self.chatDisplay)
            spacer_item.setSizeHint(QSize(0, 10))
            self.chatDisplay.addItem(spacer_item)

            # Remove the spacer item after a delay
            spacer_timer = QTimer(self)
            spacer_timer.setSingleShot(True)
            spacer_timer.timeout.connect(lambda: self.remove_message(spacer_item))
            spacer_timer.start(21000)

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
        timer.start(20000)

    def remove_message(self, item):
        """Removes a message from the chat display."""
        index = self.chatDisplay.row(item)
        if index != -1:
            self.chatDisplay.takeItem(index)
