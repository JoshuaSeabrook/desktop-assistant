from PyQt5.QtWidgets import QLineEdit


class TextInput(QLineEdit):
    def focusOutEvent(self, event):  # Override to hide the textinput when it is unfocused
        super().focusOutEvent(event)
        self.hide()
