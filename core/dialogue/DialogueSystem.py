import json

from DialogueChoice import DialogueChoice
from DialogueNode import DialogueNode
from core.dialogue.DialogueDate import DialogueDate
from core.recorder import record_audio
from core.tts_clients.Whisper.WhisperClient import WhisperClient

RETURN_KEYWORDS = {"return", "cancel", "back"}

class DialogueSystem:
    def __init__(self, json_path: str, start_point: DialogueNode, stt_client):
        self.json_path = json_path
        self.start_point = start_point
        self.stt_client = stt_client
        open(json_path, "w").close()

    def __adjust_predecessors(self, current_node: DialogueNode, next_node: DialogueNode):
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
                list(next_node.choices)[0].erase_json()

    def step(self, record: bool, path: str, node: DialogueNode) -> DialogueNode:
        print(node)
        if record:
            record_audio(5, 16_000, path)
        answer = self.stt_client.transcribe(path)
        print(f"Answer is {answer}")
        return node.advance(answer)

    # todo: Does this really belong at this abstraction level?
    def __purge_latest_json(self):
        try:
            with open(self.json_path, "r") as json_file:
                data = json.load(json_file)

            if data:
                last_key = list(data.keys())[-1]
                del data[last_key]

                with open(self.json_path, "w") as json_file:
                    json.dump(data, json_file)

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            #todo Maybe let's not just pass
            pass


    def run_files(self, paths: list[str]) -> None:
        curr_node = self.start_point
        for path in paths:
            new_node = self.step(False, path, curr_node)
            if not new_node:
                return
            else:
                self.__adjust_predecessors(curr_node, new_node)
            curr_node = new_node

    def run_record(self, path: str) -> None:
        curr_node = self.start_point
        while curr_node:
            new_node = self.step(True, path, curr_node)
            if new_node:
                self.__adjust_predecessors(curr_node, new_node)
            curr_node = new_node

    # todo: For now it's hard-coded for this particular scenario. Change this.
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


# TODO: [URGENT] Fix null recording bug!
# todo: Write out the rest of the dialogue tree.
if __name__ == "__main__":
    # Dialogue system structure setup
    ## Date choice declarations
    date_choice = DialogueDate(
        json_path="results.json",
        json_key="date",
    )
    date_prompt = "When would you like to schedule the appointment for?"
    date_choices = {date_choice}
    date_node = DialogueNode(date_choices, back_keywords=RETURN_KEYWORDS, prompt=date_prompt)

    ## Form choice declarations
    remote_choice = DialogueChoice(
        json_path="results.json",
        json_key="form",
        json_value="remote",
        keywords={"remote", "remotely", "online"},
        successor=date_node,
    )

    ## Form choice declarations
    personal_choice = DialogueChoice(
        json_path="results.json",
        json_key="form",
        json_value="personal",
        keywords={"person", "personal"},
        successor=date_node,
    )

    form_prompt = (
        "What form of appointment would you like to make?\n"
        "(Remote/in-person)"
    )
    form_choices = {remote_choice, personal_choice}
    form_node = DialogueNode(form_choices, back_keywords=RETURN_KEYWORDS, prompt=form_prompt)

    ## Specialist choice declarations
    orthodontist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="orthodontist",
        keywords={"orthodontist", "dentist", "dentists"},
        successor=form_node,
    )
    oculist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="oculist",
        keywords={"oculist", "oculists"},
        successor=form_node,
    )
    psychiatrist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="Psychiatrist",
        keywords={"psychiatrist, psychiatrists, psychiatry"},
        successor=form_node,
    )
    cardiologist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="Cardiologist",
        keywords={"cardiologist, cardiologists, cardiology"},
        successor=form_node,
    )
    laryngologist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="Laryngologist",
        keywords={"laryngologist, laryngologists, laryngology"},
        successor=form_node,
    )
    specialist_prompt = (
        "What specialist would you like to make an appointment with?\n"
        "(Orthodontist/oculist/psychiatrist/cardiologist/laryngologist/)"
    )
    specialist_choices = {
        orthodontist_choice,
        oculist_choice,
        psychiatrist_choice,
        cardiologist_choice,
        laryngologist_choice,
    }
    specialist_node = DialogueNode(specialist_choices, back_keywords=RETURN_KEYWORDS, prompt=specialist_prompt)

    ## Care choice declarations
    specialist_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="specialist",
        keywords={"specialist", "specialists", "special"},
        successor=specialist_node,
    )
    occupational_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="occupational",
        keywords={"occupational"},
        successor=form_node,
    )
    primary_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="primary",
        keywords={"primary"},
        successor=form_node,
    )
    care_prompt = (
        "What sort of physician would you like to make an appointment with?\n"
        "(Primary/special/occupational care)"
    )
    care_choices = {specialist_choice, occupational_choice, primary_choice}
    care_node = DialogueNode(care_choices, back_keywords=RETURN_KEYWORDS, prompt=care_prompt)

    ## Clinic choice declarations
    primary_clinic_choice = DialogueChoice(
        json_path="results.json",
        json_key="clinic",
        json_value="primary",
        keywords={"primary", "main", "park"},
        successor=care_node,
    )
    secondary_clinic_choice = DialogueChoice(
        json_path="results.json",
        json_key="clinic",
        json_value="secondary",
        keywords={"secondary", "yellow"},
        successor=care_node,
    )
    clinic_prompt = (
        "Which clinic are you interested in?\n"
        "(Primary at Park Street / Secondary at Yellow Street)"
    )
    clinic_choices = {primary_clinic_choice, secondary_clinic_choice}
    clinic_node = DialogueNode(clinic_choices, back_keywords=RETURN_KEYWORDS, prompt=clinic_prompt)

    ## Return choice declarations
    clinic_ret_choice = DialogueChoice(
        keywords={"return", "back", "cancel"},
        successor=clinic_node,
    )
    care_ret_choice = DialogueChoice(
        keywords={"return", "back", "cancel"},
        successor=care_node,
    )
    specialist_ret_choice = DialogueChoice(
        keywords={"return", "back", "cancel"},
        successor=specialist_node,
    )
    form_ret_choice = DialogueChoice(
        keywords={"return", "back", "cancel"},
        successor=form_node,
    )
    date_ret_choice = DialogueChoice(
        keywords={"return", "back", "cancel"},
        successor=date_node,
    )

    # Dialogue system setup
    whisper_client = WhisperClient("small.en")
    whisper_sys = DialogueSystem("results.json", clinic_node, whisper_client)

    # whisper_sys.run_record("temp_audio.wav")

    path = "audio/subjects/marcin"
    whisper_sys.run_files(
        [
            f"{path}/appointment_primary_marcin.wav",
            f"{path}/specialist_marcin.wav",
            f"{path}/orthodontist_marcin.wav",
            f"{path}/return_marcin.wav",
            f"{path}/return_marcin.wav",
            f"{path}/primary_care_marcin.wav",
            f"{path}/remote_marcin.wav",
            f"{path}/tomorrow_marcin.wav",
        ],
    )

    print(whisper_sys.interpret())
