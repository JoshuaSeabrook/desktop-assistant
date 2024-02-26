import os
import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import threading
import elevenlabs
from elevenlabs import Voice, VoiceSettings


class SpeechGenerator(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        elevenlabs.set_api_key(self.api_key)
        self.sentence_queue = []
        self.current_audio = None
        self.current_sentence = None
        self.next_audio = None

    @pyqtSlot()
    def process_next_sentence(self):
        if self.sentence_queue:
            next_sentence = self.sentence_queue[0]
            self.next_audio = elevenlabs.generate(
                text=next_sentence,
                voice=Voice(
                    voice_id="XvLR1D73tidnVz61grGk",
                    settings=VoiceSettings(
                        stability=0.7, similarity_boost=0.7, style=0.0, use_speaker_boost=True
                    )),
                model="eleven_multilingual_v2"
            )
            self.sentence_queue.pop(0)

    def play_audio(self):
        if self.sentence_queue:
            threading.Thread(target=self.process_next_sentence).start()

        self.finished.emit()  # Causes message to be displayed
        elevenlabs.play(self.current_audio, False, False)

    @pyqtSlot(str)
    def add_sentence(self, sentence):
        if not self.next_audio:
            self.process_next_sentence()
        self.sentence_queue.append(sentence)

    @pyqtSlot()
    def play_next_audio(self):
        # Main loop
        if self.next_audio:
            self.current_audio = self.next_audio
            self.current_sentence = None
            self.next_audio = None
            self.play_audio()
        elif self.sentence_queue:
            time.sleep(0.1)
        else:
            return
        self.play_next_audio()
