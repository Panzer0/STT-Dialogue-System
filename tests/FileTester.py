import random
import LinearDialogue
import os
import json
from jiwer import wer, cer


ROOT_PATH = "audio/subjects/"

SUBJECT = "norbert"

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
        self.dial_system = LinearDialogue.generate()
        self.avg_time = self.run_random(SUBJECT)

    def run_random(self, subject):
        return self.dial_system.run_files(self.subject_paths[subject])

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

    # todo: rename
    def get_selected_pairs(self):
        return {
            subject: [
                self.__interpret_path(path)
                for path in self.subject_paths[subject]
            ]
            for subject in self.subjects
        }

    def get_templates(self, subject):
        return {
            pair[0]: self.audio_lib[subject][pair[0]][pair[1]]
            for pair in self.get_selected_pairs()[subject]
        }

    def get_results(self, subject):
        return {
            pair[0]: self.dial_system.get_results()[1][pair[0]]
            for pair in self.get_selected_pairs()[subject]
        }

    def calc_total_cer(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                vals.append(cer(templates[key].lower(), results[key].lower()))
                #todo: vvv TEST CODE, REMOVE DOWN THE LINE vvv
                # if cer(templates[key].lower(), results[key].lower()) > 0:
                #     print(f"MISTAKE: '{templates[key].lower()}' | '{results[key].lower()}'")
                #todo: ^^^ TEST CODE, REMOVE DOWN THE LINE ^^^

            else:
                raise ValueError("Keys do not correspond")
        return sum(vals) / len(vals)

    def calc_total_wer(self, templates, results):
        vals = []
        for key in templates:
            if key in results:
                vals.append(wer(templates[key].lower(), results[key].lower()))
            else:
                raise ValueError("Keys do not correspond")
        return sum(vals) / len(vals)


if __name__ == "__main__":
    tester = FileTester(
        ROOT_PATH, ["clinic", "care", "specialty", "form", "date"]
    )
    print(tester.dial_system.interpret())
    print(tester.dial_system.get_results()[1])
    print(tester.get_selected_pairs())
    print(
        tester.calc_total_cer(
            tester.get_templates(SUBJECT), tester.get_results(SUBJECT)
        )
    )
    print(
        tester.calc_total_wer(
            tester.get_templates(SUBJECT), tester.get_results(SUBJECT)
        )
    )
    print(f"Average time: {tester.avg_time}")
