from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

import utils.random_utils


class AssistantMind(QObject):
    requestMessage = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.continuous_responses_enabled = False
        self.continuous_responses_frequency = 0

    @pyqtSlot()
    def start(self):
        self.requestMessage.emit("You have just been booted up, greet your user, and do nothing else.")
        self.init_timers()

    def init_timers(self):
        """Initializes the timers for the loop functions."""
        self.minute_timer = QTimer(self)
        self.minute_timer.timeout.connect(self.minute_loop)
        self.minute_timer.start(60000)  # 60-Second Timer

        self.two_minute_timer = QTimer(self)
        self.two_minute_timer.timeout.connect(self.two_minute_loop)
        self.two_minute_timer.start(120000)  # 120-Second Timer

        self.hour_timer = QTimer(self)
        self.hour_timer.timeout.connect(self.hour_loop)
        self.hour_timer.start(3600000)  # 60-Minute Timer

    def minute_loop(self):
        return

    def two_minute_loop(self):
        return

    def hour_loop(self):
        if utils.random_utils.random_true(0.2):
            self.small_talk()

    def small_talk(self):
        """Prompts the assistant to engage in small talk with the user."""
        self.requestMessage.emit("Engage in small talk with the user.")

    @pyqtSlot(bool, int)
    def set_continuous_responses(self, enabled, frequency):
        """Called from ApplicationController to enable or disable continuous responses."""
        self.continuous_responses_enabled = enabled
        self.continuous_responses_frequency = frequency

    @pyqtSlot()
    def input_enabled_event(self):
        """Called from ApplicationController when the input is enabled."""
        if self.continuous_responses_enabled:
            self.continuous_responses_timer = QTimer(self)
            self.continuous_responses_timer.setSingleShot(True)
            self.continuous_responses_timer.timeout.connect(self.continuous_responses)
            self.continuous_responses_timer.start(self.continuous_responses_frequency * 1000)


    def continuous_responses(self):
        """Prompts the assistant to continue the conversation."""
        self.requestMessage.emit("Send the next message.")

