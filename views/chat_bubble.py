from PyQt5.QtCore import QPropertyAnimation, pyqtSignal, QEasingCurve
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect

from enums import Sender


class ChatBubble(QWidget):
    fadeOutFinished = pyqtSignal()

    def __init__(self, text, sender):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.setLayout(layout)

        if sender == Sender.USER:
            self.label.setStyleSheet(
                "QLabel { background-color: #873f9d; color: white; border-radius: 10px; padding: 5px; }")
        else:  # Sender.ASSISTANT
            self.label.setStyleSheet(
                "QLabel { background-color: #333333; color: white; border-radius: 10px; padding: 5px; }")

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
