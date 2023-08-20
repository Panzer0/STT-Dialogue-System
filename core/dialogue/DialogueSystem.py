import json
import os
import time

from core.recorder import record_audio

def generate_verbal_path(path):
    directory, filename = os.path.split(path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_verbal{extension}"
    new_path = os.path.join(directory, new_filename)
    return new_path

class DialogueSystem:
    def __init__(self, json_path: str, start_point: "DialogueNode", stt_client):
        self.json_path = json_path
        self.json_path_verbal = (
            generate_verbal_path(json_path) if json_path else None
        )
        self.start_point = start_point
        self.stt_client = stt_client
        open(json_path, "w").close()

    def __adjust_predecessors(
        self, current_node: "DialogueNode", next_node: "DialogueNode"
    ):
        if next_node.back_choice:
            if next_node.back_choice.successor is None:
                # This means we're threading forward
                next_node.back_choice.successor = current_node
            else:
                # This means we're threading backwards
                current_node.back_choice.successor = None
                # todo: This assumes that the choices all have the same json_keys.
                # todo: Safe for the purpose of this project, but very bad practice.
                # todo: Perhaps come up with a better solution.
                list(next_node.choices)[0].erase_all_json()

    def step(
            self, record: bool, path: str, node: "DialogueNode"
    ) -> tuple["DialogueNode", float]:
        print(node)

        if record:
            record_audio(5, 16_000, path)

        start_time = time.time()
        answer = self.stt_client.transcribe(path)
        end_time = time.time()
        transcribe_time = end_time - start_time

        print(f"Answer is `{answer}` with time {transcribe_time}")

        return node.advance(answer), transcribe_time

    def run_files(self, paths: list[str]) -> float:
        curr_node = self.start_point
        time_sum = 0
        node_count = 0
        for path in paths:
            step_results = self.step(False, path, curr_node)
            new_node = step_results[0]
            time_sum += step_results[1]
            node_count += 1
            if not new_node:
                return time_sum / node_count
            else:
                self.__adjust_predecessors(curr_node, new_node)
            curr_node = new_node

    def run_record(self, path: str) -> None:
        curr_node = self.start_point
        while curr_node:
            new_node = self.step(True, path, curr_node)[0]
            if new_node:
                self.__adjust_predecessors(curr_node, new_node)
            curr_node = new_node

    # todo: For now it's hard-coded for this particular scenario. Change this.
    # todo: Also make it return the data in a prettier format.
    def interpret(self):
        with open(self.json_path, "r") as file:
            data = json.load(file)
        # Check for obligatory fields
        obligatory_fields = {"form", "care"}
        for field in obligatory_fields:
            if field not in data:
                raise ValueError(
                    f"Corrupt json data: Missing '{field}' parameter"
                )
        if data["care"] == "specialist" and "specialty" not in data:
            raise ValueError(
                f"Corrupt json data: Missing 'specialist' parameter"
            )

        result = ""
        for key in data.keys():
            result += f"{key}: {data[key]}\n"
        return result

    def get_results(self):
        with open(self.json_path, "r") as file:
            data = json.load(file)
        with open(self.json_path_verbal, "r") as file_verbal:
            data_verbal = json.load(file_verbal)
        return data, data_verbal

# TODO: Fix null recording bug!
