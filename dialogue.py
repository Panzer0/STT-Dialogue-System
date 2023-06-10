import recorder
from Coqui import sampleClient
import re
import time

from DialogueOption import DialogueOption
from Whisper import client
from speechbrain.pretrained import EncoderDecoderASR


palm_def = {
    "name": "Palm Tree",
    "definition": "An unbranched evergreen tree of tropical and warm regions, "
    "with a crown of very long feathered or fan-shaped leaves, "
    "and typically having old leaf scars forming a regular "
    "pattern on the trunk.",
    "emoji": "🌴"
}
evergreen_def = {
    "name": "Evergreen Tree",
    "definition": "an evergreen coniferous tree which has clusters "
    "of long needle-shaped leaves. Many kinds are grown "
    "for the soft timber, which is widely used for "
    "furniture and pulp, or for tar and turpentine.",
    "emoji": "🌲"
}
deciduous_def = {
    "name": "Deciduous  Tree",
    "definition": "A deciduous tree is a type of tree that loses its "
    "leaves seasonally. In the autumn, the leaves of "
    "deciduous trees change color and then fall off, "
    "leaving the tree without leaves for the winter. "
    "In the spring, the tree begins to grow new leaves.",
    "emoji": "🌳"
}

stop_def = {
    "name": "Stop"
}

palm_words = {"one", "on", "first", "palm"}
evergreen_words = {
    "two",
    "to",
    "too",
    "second",
    "evergreen",
    "pine",
    "pain"
}

deciduous_words = {
    "three",
    "tree",
    "he",
    "the",
    "third",
    "deciduous",
    "leaf",
    "live"}

stop_words = {"four", "fourth", "stop", "abort"}

palm_option = DialogueOption(palm_words, palm_def)
evergreen_option = DialogueOption(evergreen_words, evergreen_def)
deciduous_option = DialogueOption(deciduous_words, deciduous_def)
stop_option = DialogueOption(stop_words, stop_def)

OPTIONS = {palm_option, evergreen_option, deciduous_option, stop_option}





def match_results(results, options: set[DialogueOption]):
    for option in options:
        if option.is_mentioned(results):
            return option
    return None


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
            f"Coqui: '{results['coqui']}' in {coqui_time}\n"
            f"Whisper: '{results['whisper']}' in {whisper_time}\n"
            f"SpeechBrain: '{results['speech_brain']}' in {sb_time}"
        )

        # Try to match the recorded audio with one of the expected responses
        selection = match_results(results['whisper'], OPTIONS)
        
        if selection is None:
            print("Unrecognised command. Please, try again.")
            continue
        elif selection.definition["name"] == "Stop":
            break
        print(selection.definition["emoji"])
