from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from enums import Sender


class ChatBubble(QWidget):
    def __init__(self, text, sender):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.setLayout(layout)

        if sender == Sender.USER:
            self.label.setStyleSheet(
                "QLabel { background-color: #0078d7; color: white; border-radius: 10px; padding: 5px; }")
        else:  # Sender.ASSISTANT
            self.label.setStyleSheet(
                "QLabel { background-color: #f0f0f0; color: black; border-radius: 10px; padding: 5px; }")