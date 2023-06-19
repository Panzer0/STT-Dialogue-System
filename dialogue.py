import time


import recorder
from Coqui.CoquiClient import CoquiClient
from Whisper.WhisperClient import WhisperClient
from SpeechBrain.SBClient import SBClient
from DialogueOption import DialogueOption


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

# First option layer 
palm_words = {"1", "one", "on", "first", "palm"}
evergreen_words = {
    "2",
    "two",
    "to",
    "too",
    "second",
    "evergreen",
    "pine",
    "pain"
}
deciduous_words = {
    "3",
    "three",
    "tree",
    "he",
    "third",
    "deciduous",
    "leaf",
    "live"
}

# Second option layer
name_words = {"1", "one", "on", "first", "name"}
definition_words = {
    "2",
    "two",
    "to",
    "too",
    "second",
    "definition",
    "define"
}
emoji_words = {
    "3",
    "three",
    "tree",
    "he",
    "third",
    "emoji"
}

stop_words = {"4", "four", "fourth", "stop", "abort"}

palm_option = DialogueOption("palm", palm_words, palm_def)
evergreen_option = DialogueOption("evergreen", evergreen_words, evergreen_def)
deciduous_option = DialogueOption("deciduous", deciduous_words, deciduous_def)

name_option = DialogueOption("name", name_words)
definition_option = DialogueOption("definition", definition_words)
emoji_option = DialogueOption("emoji", emoji_words) 

stop_option = DialogueOption("stop", stop_words)

OPTIONS_1 = {palm_option, evergreen_option, deciduous_option, stop_option}
OPTIONS_2 = {name_option, definition_option, emoji_option, stop_option}





def match_results(results, options: set[DialogueOption]):
    for option in options:
        if option.is_mentioned(results):
            return option
    return None


if __name__ == "__main__":
    coqui_client = CoquiClient("Coqui/model.tflite", "Coqui/huge-vocabulary.scorer")
    whisper_client = WhisperClient("small.en") 
    sb_client = SBClient("speechbrain/asr-transformer-transformerlm-librispeech")

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

        results = dict()

        print("\nAnalysing via coqui...")
        start_time = time.time()
        results["coqui"] = coqui_client.speech_to_text("recording.wav")
        coqui_time = time.time() - start_time

        print("\nAnalysing via whisper...")
        start_time = time.time()
        results["whisper"] = whisper_client.speech_to_text("recording.wav")
        whisper_time = time.time() - start_time

        print("\nAnalysing via SpeechBrain...")
        start_time = time.time()
        results["speech_brain"] = sb_client.speech_to_text("recording.wav")
        sb_time = time.time() - start_time

        print(
            f"Coqui: '{results['coqui']}' in {coqui_time}\n"
            f"Whisper: '{results['whisper']}' in {whisper_time}\n"
            f"SpeechBrain: '{results['speech_brain']}' in {sb_time}"
        )

        # Try to match the recorded audio with one of the expected responses
        selection = match_results(results['whisper'], OPTIONS_1)
        
        if selection is None:
            print("Unrecognised command. Please, try again.")
            continue
        elif selection.definition["name"] == "Stop":
            break

        input(
            "Press enter to proceed, then say one of the following to choose information to display or abort:\n"
            "1 - Name\n"
            "2 - Definition\n"
            "3 - Emoji\n"
            "4 - Stop\n"
        )

        # Record the user for 5 seconds with a sampling rate of 16 000 Hz
        recorder.record_audio(5, 16_000)

        print("\nAnalysing via coqui...")
        start_time = time.time()
        results["coqui"] = coqui_client.speech_to_text("recording.wav")
        coqui_time = time.time() - start_time

        print("\nAnalysing via whisper...")
        start_time = time.time()
        results["whisper"] = whisper_client.speech_to_text("recording.wav")
        whisper_time = time.time() - start_time

        print("\nAnalysing via SpeechBrain...")
        start_time = time.time()
        results["speech_brain"] = sb_client.speech_to_text("recording.wav")
        sb_time = time.time() - start_time

        print(
            f"Coqui: '{results['coqui']}' in {coqui_time}\n"
            f"Whisper: '{results['whisper']}' in {whisper_time}\n"
            f"SpeechBrain: '{results['speech_brain']}' in {sb_time}"
        )

        # Try to match the recorded audio with one of the expected responses
        selection_2 = match_results(results['whisper'], OPTIONS_2)
        
        if selection_2 is None:
            print("Unrecognised command. Please, try again.")
            continue
        elif selection_2.name == "stop":
            break

        print(selection.definition[selection_2.name] + '\n')
