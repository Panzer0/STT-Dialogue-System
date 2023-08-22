import random
from datetime import datetime

import LinearDialogue
import os
import json
from jiwer import wer, cer
from core.dialogue.DialogueDate import interpret_date
import parsedatetime as pdt


ROOT_PATH = "audio/subjects/"
NODE_NAMES = ["clinic", "care", "specialty", "form", "date"]


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

    def run_subject(self, subject: str) -> dict:
        dial_system = LinearDialogue.generate()
        avg_time = dial_system.run_files(self.subject_paths[subject])
        templates = self.get_templates(subject)
        results = self.get_results_verbal(subject, dial_system)
        avg_cer = self.calc_avg_cer(templates, results)
        avg_wer = self.calc_avg_wer(templates, results)
        avg_cher = self.calc_cher(subject, dial_system)
        return {
            "avg_time": avg_time,
            "avg_cer": avg_cer,
            "avg_wer": avg_wer,
            "avg_cher": avg_cher,
        }

    def run_total(self):
        totals = {"avg_time": 0, "avg_cer": 0, "avg_wer": 0, "avg_cher": 0}
        for subject in self.subjects:
            totals = sum_dicts(totals, self.run_subject(subject))
        return divide_dict(totals, len(self.subjects))

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
    def calc_avg_cer(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                vals.append(cer(templates[key].lower(), results[key].lower()))
                # todo: vvv TEST CODE, REMOVE DOWN THE LINE vvv
                # if cer(templates[key].lower(), results[key].lower()) > 0:
                #     print(f"MISTAKE: '{templates[key].lower()}' | '{results[key].lower()}'")
                # todo: ^^^ TEST CODE, REMOVE DOWN THE LINE ^^^

            else:
                raise ValueError("Keys do not correspond")
        return sum(vals) / len(vals)

    # word error rate
    def calc_avg_wer(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                vals.append(wer(templates[key].lower(), results[key].lower()))
            else:
                raise ValueError("Keys do not correspond")
        return sum(vals) / len(vals)

    # choice error rate
    def calc_cher(self, subject, dial_system):
        results = dial_system.get_results()
        err_count = 0

        for node in results[0]:
            if node == "date":
                choice = interpret_date(results[1][node])
                expected_choice = interpret_date(
                    self.audio_lib[subject][node]["date.wav"]
                )
            else:
                choice = results[0][node] + ".wav"
                expected_choice = self.get_selected_choice(subject, node)

            if choice != expected_choice:
                err_count += 1

        return err_count / len(results[0])


if __name__ == "__main__":
    tester = FileTester(ROOT_PATH, NODE_NAMES)
    print(tester.run_total())
