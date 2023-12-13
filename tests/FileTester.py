import random
import LinearDialogue
import os
import json
from jiwer import wer, cer
from core.dialogue.DialogueDate import interpret_date
import parsedatetime as pdt
import pandas as pd


from core.tts_clients.Coqui.CoquiClient import CoquiClient
from core.tts_clients.SpeechBrain.SBClient import SBClient
from core.tts_clients.Whisper.WhisperClient import WhisperClient

ROOT_PATH = "audio/subjects/"
NODE_NAMES = ["clinic", "care", "specialty", "form", "date"]

COQUI = CoquiClient("core/tts_clients/Coqui/model.tflite", "core/tts_clients/Coqui/huge-vocabulary.scorer")
WHISPER = WhisperClient("small.en")
SB = SBClient("speechbrain/asr-transformer-transformerlm-librispeech")


def sum_dicts(dict1: dict, dict2: dict) -> dict:
    result = {}
    for key in dict1:
        result[key] = dict1[key] + dict2[key]
    return result


def divide_dict(dividend: dict, divisor) -> dict:
    if divisor == 0:
        raise ZeroDivisionError("Can't divide by zero.")
    result = {}
    for key in dividend:
        result[key] = dividend[key] / divisor
    return result

def strip_path_ext(path: str) -> str:
    directory, filename = os.path.split(path)
    return os.path.splitext(filename)[0]

class FileTester:
    # todo: Add tts_client argument
    def __init__(self, root_path, node_names: list[str]):
        self.root_path = root_path
        self.subjects = self.get_subjects()
        self.audio_lib = {
            subject: self.generate_audio_data(subject)
            for subject in self.subjects
        }
        self.subject_paths = {
            subject: self.__generate_audio_paths(
                subject, self.audio_lib[subject], node_names
            )
            for subject in self.subjects
        }
        self.out_data = {
            'Client': [],
            'Subject': [],
            'Node': [],
            'WER': [],
            'CER': [],
            'CHER': [],
            'Runtime': []
        }

    def run_subject(self, subject: str, client) -> None:
        dial_system = LinearDialogue.generate(client)
        times = dial_system.run_files(self.subject_paths[subject])
        templates = self.get_templates(subject)
        results = self.get_results_verbal(subject, dial_system)
        cers = self.calc_cers(templates, results)
        wers = self.calc_wers(templates, results)
        chers = self.calc_chers(subject, dial_system)
        nodes = [strip_path_ext(path) for path in self.subject_paths[subject]]

        if not len(cers) == len(wers) == len(chers) == len(times) == len(nodes):
            raise AssertionError("Inconsistent data count")

        self.out_data['Client'].extend([client.name] * len(times))
        self.out_data['Subject'].extend([subject] * len(times))
        self.out_data['Node'].extend(nodes)
        self.out_data['WER'].extend(wers)
        self.out_data['CER'].extend(cers)
        self.out_data['CHER'].extend(chers)
        self.out_data['Runtime'].extend(times)

    def run_total(self, client) -> None:
        for subject in self.subjects:
            print(f"Subject: {subject.upper()}")
            self.run_subject(subject, client)

    def get_subjects(self):
        return [subject for subject in os.listdir(self.root_path)]

    def generate_audio_data(self, subject):
        audio_data = {}

        for node_name in os.listdir(self.root_path + subject):
            node_path = os.path.join(self.root_path + subject, node_name)
            if os.path.isdir(node_path):
                contents_file = os.path.join(node_path, "contents.json")
                if os.path.exists(contents_file):
                    with open(contents_file, "r") as f:
                        contents_data = json.load(f)
                    audio_data[node_name] = contents_data

        return audio_data

    def __generate_audio_path(self, subject: str, node: str, audio_data):
        path = self.root_path + subject
        file_name = random.choice(list(audio_data[node].keys()))
        return f"{path}/{node}/{file_name}"

    def __generate_audio_paths(
        self, subject: str, audio_data, nodes: list[str]
    ):
        return [
            self.__generate_audio_path(subject, node, audio_data)
            for node in nodes
        ]

    def __interpret_path(self, path):
        components = path.split("/")
        return components[-2], components[-1]

    def get_selected_choice(self, subject, node):
        pairs = self.get_selected_pairs()[subject]
        for pair in pairs:
            if pair[0] == node:
                return pair[1]

    # todo: rename
    def get_selected_pairs(self):
        return {
            subject: {
                self.__interpret_path(path)
                for path in self.subject_paths[subject]
            }
            for subject in self.subjects
        }

    def get_templates(self, subject):
        return {
            pair[0]: self.audio_lib[subject][pair[0]][pair[1]]
            for pair in self.get_selected_pairs()[subject]
        }

    def get_results_verbal(self, subject, dial_system):
        return {
            pair[0]: dial_system.get_results()[1][pair[0]]
            for pair in self.get_selected_pairs()[subject]
        }

    # character error rate
    def calc_cers(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                new_cer = cer(templates[key].lower(), results[key].lower())
                vals.append(new_cer)
                # # todo: vvv TEST CODE, REMOVE DOWN THE LINE vvv
                # if new_cer > 0:
                #     print(
                #         f"MISTAKE: '{templates[key].lower()}' | '{results[key].lower()}'"
                #     )
                # # todo: ^^^ TEST CODE, REMOVE DOWN THE LINE ^^^
            else:
                raise ValueError("Keys do not correspond")
        return vals

    # word error rate
    def calc_wers(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                new_wer = wer(templates[key].lower(), results[key].lower())
                vals.append(new_wer)
            else:
                raise ValueError("Keys do not correspond")
        return vals

    # choice error rate
    def calc_chers(self, subject, dial_system):
        results = dial_system.get_results()
        vals = []

        for node in results[0]:
            if node == "date":
                choice = interpret_date(results[1][node])
                expected_choice = interpret_date(
                    self.audio_lib[subject][node]["date.wav"]
                )
            else:
                choice = results[0][node] + ".wav"
                expected_choice = self.get_selected_choice(subject, node)
            vals.append(0) if choice == expected_choice else vals.append(1)

        return vals


if __name__ == "__main__":
    clients = [COQUI, WHISPER, SB]
    dataframes = []
    for client in clients:
        tester = FileTester(ROOT_PATH, NODE_NAMES)
        tester.run_total(client)
        dataframes.append(pd.DataFrame(tester.out_data))

    for dataframe in dataframes:
        print(dataframe)
        print(dataframe.info())

    combined_df = pd.concat(dataframes, ignore_index=True)
    average_df = combined_df.groupby('Client').agg({
        'WER': 'mean',
        'CER': 'mean',
        'CHER': 'mean',
        'Runtime': 'mean'
    })

    print(average_df)