import os
import tempfile
import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
import threading
from playsound import playsound

from utils.settings_manager import SettingsManager
from openai import OpenAI


class SpeechGenerator(QObject):
    finished = pyqtSignal()
    start_speaking = pyqtSignal()
    finished_speaking = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_playing_audio = None
        self.sentence_queue = []
        self.current_audio = None
        self.current_sentence = None
        self.audio_queue = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_next_audio)
        self.timer.start(1000)
        self.total_chars = 0

    @pyqtSlot()
    def process_sentences(self):
        """Processes the sentences in the queue and generates audio for them."""
        if self.sentence_queue:
            self.total_chars += len(self.sentence_queue[0])
            try:
                next_sentence = self.sentence_queue[0]
                client = OpenAI()

                response = client.audio.speech.create(
                    model="tts-1-hd",
                    voice="nova",
                    input=next_sentence,
                )
                temp_dir = tempfile.gettempdir()
                temp_file = tempfile.mktemp(suffix=".mp3", dir=temp_dir)

                response.stream_to_file(temp_file)
                self.sentence_queue.pop(0)
                self.audio_queue.append(temp_file)
            except Exception as e:
                SettingsManager().update_setting("assistant_chat_bubbles", True)
                if not self.is_playing_audio:
                    threading.Thread(target=self.play_audio, args=(False, self.sentence_queue.pop(0))).start()

    def play_audio(self, audio=True, sentence=None):
        """Plays the audio from the audio queue."""
        if audio:
            while self.audio_queue:
                self.finished.emit()  # Signal that the audio has finished playing
                self.start_speaking.emit()
                next_audio_to_play = self.audio_queue.pop(0)
                playsound(next_audio_to_play)
                os.remove(next_audio_to_play)
                self.finished_speaking.emit()
                time.sleep(0.5)
        else:  # If the audio is not in the queue for whatever reason
            self.is_playing_audio = True
            self.start_speaking.emit()
            self.finished.emit()  # Signal that the audio has finished playing
            time.sleep(len(sentence) / 25)  # Wait depending on the length of the sentence, to simulate the time it would take to say it
            self.finished_speaking.emit()
        self.is_playing_audio = False

    @pyqtSlot(str)
    def add_sentence(self, sentence):
        """Adds a sentence to the queue."""
        self.sentence_queue.append(sentence)
        if not self.audio_queue:
            self.process_sentences()

    @pyqtSlot()
    def play_next_audio(self):
        """Continually called by a timer, checks if there is audio to play."""
        # Main loop
        if self.audio_queue and not self.is_playing_audio:
            self.is_playing_audio = True  # Set the flag to indicate that audio is being played
            threading.Thread(target=self.play_audio).start()
        elif not self.audio_queue:
            self.process_sentences()
