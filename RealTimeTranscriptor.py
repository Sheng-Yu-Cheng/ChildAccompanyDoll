import threading
import whisper
import pyaudio
import numpy
import wave
import os
import uuid

class RealTimeTranscriptor(threading.Thread):
    def __init__(self, 
            chunk_size: int = 5000,    # transcription chunk size (ms)
            input_rate: int = 16000,   # pyaudio: input rate (samples per second)
            buffer_size: int = 1024,   # pyaudio: size of a audio sample buffer
            channel_amount: int = 1,   # pyaudio: microphone channel amount
            model_size: str = "turbo"   # whisper: transcription model size
        ):
        # include all threading properties
        super().__init__()
        # pyaudio microphone
        self.chunk_size = chunk_size
        self.input_rate = input_rate
        self.buffer_size = buffer_size
        self.channel_amount = channel_amount
        self.__pyaudio = pyaudio.PyAudio()
        self.input_stream = self.__pyaudio.open(
            format = pyaudio.paInt16, 
            channels = self.channel_amount, 
            rate = self.input_rate, 
            input = True, 
            frames_per_buffer = self.buffer_size,
            input_device_index = 2
        )
        # whisper setting
        self.transcriptor = whisper.load_model(model_size)
        # transcription process flag
        self.running: bool = True
    def run(self):
        print("🔴 Recording... Press Ctrl+C to stop.")
        while self.running:
            frames = []
            for _ in range(0, int(self.input_rate / self.buffer_size * self.chunk_size / 1000)):
                data = self.input_stream.read(self.buffer_size)
                frames.append(numpy.frombuffer(data, dtype = numpy.int16))
            audio_np = numpy.concatenate(frames)
            temp_filename = f"temp_{uuid.uuid4()}.wav"
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channel_amount)
                wf.setsampwidth(self.__pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.input_rate)
                wf.writeframes(audio_np.tobytes())
            result = self.transcriptor.transcribe(
                temp_filename, 
                condition_on_previous_text = False,
                no_speech_threshold = 0.2  # increase sensitivity to silence)
            )
            if not result["text"].strip():
                print("🤔 Not hearing anything...")
            else:
                print("🗣️", result["text"])
            os.remove(temp_filename)

    def terminate(self):
        self.running = False

a = RealTimeTranscriptor()
a.start()
from time import sleep
try:
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    print("🛑 Exiting...")
    a.terminate()
    a.join()