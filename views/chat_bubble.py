import markdown
from PyQt5.QtCore import QPropertyAnimation, pyqtSignal, QEasingCurve, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect

from enums import Sender


class ChatBubble(QWidget):
    fadeOutFinished = pyqtSignal()

    def __init__(self, text, sender):
        super().__init__()
        layout = QVBoxLayout()

        # Convert Markdown text to HTML
        html_text = markdown.markdown(text)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setText(html_text)
        self.label.setFixedWidth(self.width() - 80)  # Fixes weird text wrapping height issues
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Apply CSS styles for USER and ASSISTANT differently
        user_style = "QLabel { background-color: #873f9d; color: white; border-radius: 10px; padding: 5px; }"
        assistant_style = "QLabel { background-color: #333333; color: white; border-radius: 10px; padding: 5px; }"

        if sender == Sender.USER:
            self.label.setStyleSheet(user_style)
        else:  # Sender.ASSISTANT
            self.label.setStyleSheet(assistant_style)

        self.label.setTextFormat(Qt.RichText)

    def fade_out(self):
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacityEffect)

        self.animation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # Smooth transition

        self.animation.finished.connect(self.fade_out_finished)
        self.animation.start(QPropertyAnimation.DeleteWhenStopped)

    def fade_out_finished(self):
        self.fadeOutFinished.emit()
