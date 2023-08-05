import sounddevice as sd
import struct

MAX_SHORT_INT = 32767

def save_audio(recording, fs, filename):
    with open(filename, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<L", 36 + len(recording) * 2))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<LHHLLHH", 16, 1, 1, fs, fs * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<L", len(recording) * 2))

        for sample in recording:
            f.write(struct.pack("<h", int(sample)))

def record_audio(length, fs, filename="recording.wav"):
    duration = int(length * fs)
    print("Recording...")
    try:
        recording = sd.rec(duration, samplerate=fs, channels=1, blocking=False)

        while input("Type 'stop' to stop the recording: ").lower() != "stop":
            pass

        sd.stop()
        print("Recording stopped")
        recording = recording / max(abs(recording)) * MAX_SHORT_INT
        save_audio(recording, fs, filename)

    except KeyboardInterrupt:
        sd.stop()
        print("Recording stopped due to keyboard interrupt.")
    except Exception as e:
        print("An error occurred during recording:", e)

if __name__ == "__main__":
    record_audio(6, 16000)
    print("I am recorder's main")

