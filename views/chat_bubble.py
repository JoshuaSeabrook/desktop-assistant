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
        self.label.setFixedWidth(self.width() - 68)  # Fixes weird text wrapping height issues
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        user_style = """
        QLabel {
            background-color: rgba(51, 51, 51, 230); /* #333333 with 90% transparency */
            color: white;
            border-radius: 3px;
            padding: 5px;
            font-size: 16px;
        }
        """

        assistant_style = """
        QLabel {
            background-color: rgba(74, 65, 177, 230); /* #4a41b1 with 90% transparency */
            color: white;
            border-radius: 3px;
            padding: 5px;
            font-size: 16px;
        }
        """

        if sender == Sender.USER:
            self.label.setStyleSheet(user_style)
        else:  # Sender.ASSISTANT
            self.label.setStyleSheet(assistant_style)

        self.label.setTextFormat(Qt.RichText)

    def fade_out(self):
        """Fades the chat bubble out."""
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
        """Emits the fadeOutFinished signal."""
        self.fadeOutFinished.emit()
