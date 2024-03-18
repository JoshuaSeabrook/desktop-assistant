from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QSize, QEasingCurve
from PyQt5.QtGui import QPainter, QImage, QPainterPath
from PyQt5.QtWidgets import QWidget


class AssistantIcon(QWidget):
    def __init__(self, parent=None, imagePath="assets/icons/icon.png", fixedCenter=QPoint(560, 35)):
        super().__init__(parent)
        self.fixedCenter = fixedCenter
        self.updatePositionForCenter()
        self.setMinimumSize(50, 50)
        self.setMaximumSize(55, 55)
        self.parent = parent

        self.imagePath = imagePath
        self.anim_in = QPropertyAnimation(self, b'pos')
        self.anim_out = QPropertyAnimation(self, b'pos')
        self.anim_expand = QPropertyAnimation(self, b'size')
        self.anim_shrink = QPropertyAnimation(self, b'size')
        self.anim_expand.valueChanged.connect(self.updatePositionForCenter)
        self.anim_shrink.valueChanged.connect(self.updatePositionForCenter)
        self.setWindowOpacity(0.1)
        self.isPulsing = False
        if parent:
            self.move(parent.width(), 0)
        self.setup_pulse_animation()

    def updatePositionForCenter(self):
        """Updates the position of the widget to ensure it remains centered."""
        newTopLeftX = self.fixedCenter.x() - self.width() / 2
        newTopLeftY = self.fixedCenter.y() - self.height() / 2
        self.move(int(newTopLeftX), int(newTopLeftY))

    def resizeEvent(self, event):
        """Overridden to ensure the widget remains centered when resized."""
        super().resizeEvent(event)
        self.updatePositionForCenter()

    def setup_pulse_animation(self):
        """Sets up the pulse animation for the assistant icon."""
        self.anim_expand.setDuration(50)
        self.anim_expand.setStartValue(self.size())
        self.anim_expand.setEndValue(QSize(55, 55))
        self.anim_expand.setEasingCurve(QEasingCurve.InOutSine)

        self.anim_shrink.setDuration(50)
        self.anim_shrink.setStartValue(QSize(55, 55))
        self.anim_shrink.setEndValue(QSize(50, 50))
        self.anim_shrink.setEasingCurve(QEasingCurve.InOutSine)

        self.anim_expand.finished.connect(lambda: self.anim_shrink.start() if self.isPulsing else None)
        self.anim_shrink.finished.connect(lambda: self.anim_expand.start() if self.isPulsing else None)

    def start_pulse_animation(self):
        """Starts the pulse animation for the assistant icon."""
        if not self.isPulsing:
            self.isPulsing = True
            self.anim_expand.start()

    def stop_pulse_animation(self):
        """Stops the pulse animation for the assistant icon."""
        if self.isPulsing:
            self.isPulsing = False
            self.anim_expand.stop()
            self.anim_shrink.stop()
            # Reset size
            self.resize(50, 50)

    def paintEvent(self, event):
        """Overridden to paint the assistant icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setOpacity(0.9)

        if self.imagePath:
            image = QImage(self.imagePath)
            image = image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_x = int((self.width() - image.width()) / 2)
            img_y = int((self.height() - image.height()) / 2)

            path = QPainterPath()
            path.addEllipse(0, 0, self.width(), self.height())
            painter.setClipPath(path)

            painter.drawImage(img_x, img_y, image)
        else:
            super().paintEvent(event)

    def animate_in(self):
        """Animates the assistant icon into view."""
        endX = int(self.fixedCenter.x() - self.width() / 2)
        endY = int(self.fixedCenter.y() - self.height() / 2)
        self.anim_in.setDuration(100)
        self.anim_in.setStartValue(QPoint(int(self.fixedCenter.x() + self.width()),
                                          int(self.y())))
        self.anim_in.setEndValue(QPoint(endX, endY))
        self.anim_in.start()

    def animate_out(self):
        """Animates the assistant icon out of view."""
        startX = int(self.fixedCenter.x() - self.width() / 2)
        startY = int(self.fixedCenter.y() - self.height() / 2)
        self.anim_out.setDuration(100)
        self.anim_out.setStartValue(QPoint(startX, startY))
        self.anim_out.setEndValue(QPoint(int(self.fixedCenter.x() + self.width()),
                                         int(self.y())))
        self.anim_out.start()


