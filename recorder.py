import sounddevice as sd
import struct
from Coqui import sampleClient

MAX_SHORT_INT = 32767

def save_audio(recording, fs):
    with open("recording.wav", "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<L", 36 + len(recording) * 2))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<LHHLLHH", 16, 1, 1, fs, fs * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<L", len(recording) * 2))

        for sample in recording:
            f.write(struct.pack("<h", int(sample)))

def record_audio(length, fs):
    duration = int(length * fs)
    print("Recording...")
    recording = sd.rec(duration, samplerate=fs, channels=1, blocking=False)

    try:
        while input("Type 'stop' to stop the recording: ").lower() != "stop":
            pass
    except KeyboardInterrupt:
        pass

    sd.stop()
    print("Recording stopped")
    recording = recording / max(abs(recording)) * MAX_SHORT_INT
    save_audio(recording, fs)

if __name__ == "__main__":
    record_audio(6, 16000)
    sampleClient.speech_to_text("recording.wav", "model.tflite", "large_vocabulary.scorer")

