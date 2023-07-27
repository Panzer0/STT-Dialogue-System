from DialogueChoice import DialogueChoice
from DialogueNode import DialogueNode
from core.recorder import record_audio
from core.tts_clients.Whisper.WhisperClient import WhisperClient


class DialogueSystem:
    def __init__(self, json_path: str, start_point: DialogueNode, stt_client):
        self.json_path = json_path
        self.start_point = start_point
        self.stt_client = stt_client
        open(json_path, "w").close()

    def step(self, record: bool, path: str, node: DialogueNode) -> DialogueNode:
        if record:
            record_audio(5, 16_000, path)
        answer = self.stt_client.transcribe(path)
        return node.advance(answer)

    def run_files(self, paths: list[str]) -> None:
        node = self.start_point
        for path in paths:
            node = self.step(False, path, node)
            if not node:
                return

    def run_record(self, path: str) -> None:
        node = self.start_point
        while node:
            node = self.step(True, path, node)


# TODO: [URGENT] Fix null recording bug!
# todo: Write out the rest of the dialogue tree.
if __name__ == "__main__":
    # Dialogue system structure setup
    ## Specialist choice declarations
    orthodontist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="orthodontist",
        keywords={"orthodontist", "dentist"},
    )
    oculist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="oculist",
        keywords={"oculist"},
    )
    psychiatrist_choice = DialogueChoice(
        json_path="results.json",
        json_key="specialty",
        json_value="Psychiatrist",
        keywords={"psychiatrist"},
    )
    specialist_choices = {
        orthodontist_choice,
        oculist_choice,
        psychiatrist_choice,
    }
    specialist_node = DialogueNode(specialist_choices)

    ## Care choice declarations
    specialist_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="specialist",
        keywords={"specialist", "specialists"},
        successor=specialist_node,
    )
    occupational_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="occupational",
        keywords={"occupational"},
    )
    primary_choice = DialogueChoice(
        json_path="results.json",
        json_key="care",
        json_value="primary",
        keywords={"primary"},
    )
    care_choices = {specialist_choice, occupational_choice, primary_choice}
    care_node = DialogueNode(care_choices)

    whisper_client = WhisperClient("small.en")
    whisper_sys = DialogueSystem("results.json", care_node, whisper_client)
    whisper_sys.run_record("temp_audio.wav")
    # whisper_sys.run_files(["temp_audio.wav"])
