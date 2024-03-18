import os
import queue
import tempfile

import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from openai import OpenAI
from scipy.io.wavfile import write


class Transcriber(QThread):
    transcription_complete = pyqtSignal(str)  # Signal to emit the transcribed text

    def __init__(self, samplerate=44100, channels=1, model="whisper-1", silence_threshold=0.01, silence_duration=1.5,
                 parent=None):
        super(Transcriber, self).__init__(parent)
        self.speech_threshold = 0.01
        self.base_silence_duration = 1
        self.max_silence_duration = 5
        self.samplerate = samplerate
        self.channels = channels
        self.model = model
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.client = OpenAI()  # Initialize OpenAI client here
        self.audio_queue = queue.Queue()

    def audio_callback(self, indata):
        """Callback function to process audio data from the microphone."""
        self.audio_queue.put(indata.copy())

    def record_audio(self):
        """
        Records audio from the microphone and returns the audio data.

        Designed to wait until it detects enough volume to start recording, then waits for a period of silence to stop recording.
        """
        with sd.InputStream(callback=self.audio_callback, channels=self.channels, samplerate=self.samplerate):
            recorded_audio = []
            silence_counter = 0
            speech_detected = False
            while True:
                indata = self.audio_queue.get()
                if indata.any():
                    volume = np.sqrt(np.mean(indata ** 2))  # RMS value of the audio data, used to compare volume
                    if volume > self.speech_threshold:
                        speech_detected = True
                        recorded_audio.append(indata)
                        silence_counter = 0
                    elif volume < self.silence_threshold and speech_detected:
                        scaling_factor = 0.2
                        current_silence_duration = min(  # Scale the required silence duration based on the length of the recording
                            self.max_silence_duration,
                            self.base_silence_duration + (len(recorded_audio) / self.samplerate) * scaling_factor
                        )
                        silence_limit = current_silence_duration * self.samplerate / 1024
                        silence_counter += 1
                        if silence_counter > silence_limit:
                            break
                    elif speech_detected:
                        recorded_audio.append(indata)
                else:
                    break
            audio_data = np.concatenate(recorded_audio, axis=0)
        return audio_data

    def transcribe_audio(self, audio_data):
        """Transcribes the given audio data and returns the transcribed text."""
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.mktemp(suffix=".wav", dir=temp_dir)
        write(temp_file, self.samplerate, audio_data)  # Saves the audio data to a temporary file, to be used for transcription

        try:
            with open(temp_file, "rb") as tmpfile:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=tmpfile,
                    language="en"
                )
                return transcription.text
        finally:
            os.remove(temp_file)  # Remove the temporary file after transcription

    @pyqtSlot()
    def transcribe_from_microphone(self):
        """Function called by ApplicationController. Records audio from the microphone and transcribes it."""
        audio_data = self.record_audio()
        transcription_text = self.transcribe_audio(audio_data)
        print("User input: " + transcription_text)
        self.transcription_complete.emit(transcription_text)
