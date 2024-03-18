from PyQt5.QtWidgets import QLineEdit, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal


class TextInput(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacityEffect)

        self.fadeAnimation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.fadeAnimation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeAnimation.setDuration(500)
        self._isFadingOut = False

        # Ensure the widget starts hidden and with 0 opacity
        self.opacityEffect.setOpacity(0.0)
        super().setVisible(False)

    def setVisible(self, visible):
        """Overridden to add fade-in and fade-out effects."""
        if visible:
            super().setVisible(True)
            self.fadeAnimation.setStartValue(self.opacityEffect.opacity())
            self.fadeAnimation.setEndValue(1.0)
            self.fadeAnimation.finished.connect(self._resetFadeOutFlag)
            self.fadeAnimation.start()
        else:
            if not self._isFadingOut and self.isVisible():
                self._isFadingOut = True
                self.fadeAnimation.setStartValue(self.opacityEffect.opacity())
                self.fadeAnimation.setEndValue(0.0)
                self.fadeAnimation.finished.connect(self._hideAndResetFadeOutFlag)
                self.fadeAnimation.start()

    def _hideAndResetFadeOutFlag(self):
        """Hides the widget and resets the fade-out flag."""
        super().setVisible(False)
        self._resetFadeOutFlag()

    def _resetFadeOutFlag(self):
        """Resets the fade-out flag and disconnects the animation's finished signal."""
        self._isFadingOut = False
        self.fadeAnimation.finished.disconnect()

    def focusOutEvent(self, event):
        """Hides the widget when focus is lost. (The user clicks onto something else)"""
        super().focusOutEvent(event)
        self.setVisible(False)
