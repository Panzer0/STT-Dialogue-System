import sounddevice as sd
import wave
import numpy as np
import threading
import queue

MAX_SHORT_INT = 32767


def save_audio(recording, fs, filename):
    if recording is None:
        raise ValueError("No recording data found.")

    # Probably unneeded
    recording = recording / np.max(np.abs(recording)) * MAX_SHORT_INT
    recording = recording.astype(np.int16)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())


def record_audio_thread(q, duration, fs):
    recording = sd.rec(duration, samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    q.put(recording)


def record_audio(length, fs, filename="recording.wav"):
    duration = int(length * fs)
    print("Initialising recorder...")
    try:
        q = queue.Queue()
        recording_thread = threading.Thread(
            target=record_audio_thread, args=(q, duration, fs)
        )
        recording_thread.start()
        print("Recording started. Type 'stop' to stop the recording.")

        while input().lower() != "stop":
            pass

        recording_thread.join()
        recording = q.get()

        print("Recording stopped")
        save_audio(recording, fs, filename)

    except KeyboardInterrupt:
        print("Recording stopped due to keyboard interrupt.")
    except Exception as e:
        print("An error occurred during recording:", e)
