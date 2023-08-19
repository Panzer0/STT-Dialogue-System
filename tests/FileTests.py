import random
from collections import OrderedDict

import LinearDialogue
import os
import json


ROOT_PATH = "audio/subjects/"

def generate_audio_data(directory: str):
    audio_data = {}

    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        if os.path.isdir(folder_path):
            contents_file = os.path.join(folder_path, "contents.json")
            if os.path.exists(contents_file):
                with open(contents_file, "r") as f:
                    contents_data = json.load(f)
                audio_data[folder_name] = contents_data

    return audio_data

def generate_audio_path(subject: str, category: str, audio_data):
    path = ROOT_PATH + subject
    file_name = random.choice(list(audio_data[category].keys()))
    return f"{path}/{category}/{file_name}"

def generate_audio_paths(subject: str, audio_data, nodes: list[str]):
    return [generate_audio_path(subject, node, audio_data) for node in nodes]


if __name__ == '__main__':
    dial_system = LinearDialogue.generate()
    subject = "marcin"
    path = ROOT_PATH + subject
    audio_data = generate_audio_data(path)
    nodes = ["clinic", "care", "specialty", "form", "date"]
    dial_system.run_files(
        generate_audio_paths(subject, audio_data, nodes)
    )


    print(dial_system.interpret())

    # reference = "give me a specialist"
    # hypothesis = "give me a special list"
    #
    # cer_val = cer(reference, hypothesis)
    # wer_val = wer(reference, hypothesis)
    #
    # print(f"cer: {cer_val}\n" f"wer: {wer_val}")
