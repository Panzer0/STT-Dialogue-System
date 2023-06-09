import recorder
from Coqui import sampleClient
import re
import time
from Whisper import client
from speechbrain.pretrained import EncoderDecoderASR


palmTree = {
    "name": "Palm Tree",
    "definition": "An unbranched evergreen tree of tropical and warm regions, "
    "with a crown of very long feathered or fan-shaped leaves, "
    "and typically having old leaf scars forming a regular "
    "pattern on the trunk.",
    "emoji": "🌴",
}
evergreenTree = {
    "name": "Evergreen Tree",
    "definition": "an evergreen coniferous tree which has clusters "
    "of long needle-shaped leaves. Many kinds are grown "
    "for the soft timber, which is widely used for "
    "furniture and pulp, or for tar and turpentine.",
    "emoji": "🌲",
}
deciduousTree = {
    "name": "Deciduous  Tree",
    "definition": "A deciduous tree is a type of tree that loses its "
    "leaves seasonally. In the autumn, the leaves of "
    "deciduous trees change color and then fall off, "
    "leaving the tree without leaves for the winter. "
    "In the spring, the tree begins to grow new leaves.",
    "emoji": "🌳",
}

palm_words = ["one", "on", "first", "palm"]
evergreen_words = [
    "two",
    "to",
    "too",
    "second",
    "evergreen",
    "pine",
    "pain",
]
deciduous_words = [
    "three",
    "tree",
    "he",
    "the",
    "third",
    "deciduous",
    "leaf",
    "live",
]
stop_words = ["four", "fourth", "stop", "abort"]


def containsWord(string, word):
    return re.search(r"\b" + word + r"\b", string)


def containsAny(string, words):
    return any(containsWord(string, word) for word in words)




if __name__ == "__main__":
    while True:
        input(
            "Press enter to proceed, then say one of the following to choose tree type or abort:\n"
            "1 - Palm\n"
            "2 - Evergreen\n"
            "3 - Deciduous\n"
            "4 - Stop\n"
        )

        # Record the user for 5 seconds with a sampling rate of 16 000 Hz
        recorder.record_audio(5, 16_000)

        # Convert the recorded audio into text
        results = dict()

        print("\nAnalysing via coqui...")
        start_time = time.time()
        results["coqui"] = sampleClient.speech_to_text(
            "recording.wav",
            "Coqui/model.tflite",
            "Coqui/large_vocabulary.scorer",
        )
        end_time = time.time()
        coqui_time = end_time - start_time

        print("\nAnalysing via whisper...")
        start_time = time.time()
        results["whisper"] = client.speech_to_text("recording.wav", "small.en")
        end_time = time.time()
        whisper_time = end_time - start_time

        print("\nAnalysing via SpeechBrain...")
        start_time = time.time()
        sb_model = EncoderDecoderASR.from_hparams(
            "speechbrain/asr-transformer-transformerlm-librispeech", 
            run_opts={"device":"cuda"} 
        )
        results["speech_brain"] = sb_model.transcribe_file("recording.wav")
        end_time = time.time()
        sb_time = end_time - start_time

        print(
            f"Coqui: '{results['coqui']} in {coqui_time}'\n"
            f"Whisper: '{results['whisper']} in {whisper_time}'\n"
            f"SpeechBrain: '{results['speech_brain']} in {sb_time}'"
        )

        # Try to match the recorded audio with one of the expected responses
        if containsAny(results["coqui"], palm_words):
            selection = palmTree
        elif containsAny(results["coqui"], evergreen_words):
            selection = evergreenTree
        elif containsAny(results["coqui"], deciduous_words):
            selection = deciduousTree
        elif containsAny(results["coqui"], stop_words):
            print("Break!")
            break
        else:
            print(f"\nUnrecognised command. Try again.\n")
            continue

        print(selection["emoji"])
