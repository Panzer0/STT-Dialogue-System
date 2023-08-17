# todo: Implement a better way to run tests
# todo: Implement WER, CER and path validity tests
from jiwer import wer, cer

from core.dialogue.DialogueChoice import DialogueChoice
from core.dialogue.DialogueDate import DialogueDate
from core.dialogue.DialogueNode import DialogueNode
from core.dialogue.DialogueSystem import DialogueSystem
from core.tts_clients.Whisper.WhisperClient import WhisperClient


RETURN_KEYWORDS = {"return", "cancel", "back"}

if __name__ == '__main__':

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
        keywords={"remote", "remotely", "online", "virtual"},
        successor=date_node,
    )

    ## Form choice declarations
    personal_choice = DialogueChoice(
        json_path="results.json",
        json_key="form",
        json_value="personal",
        keywords={"person", "personal", "personally"},
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
        keywords={"specialist", "specialists", "special", "specialized", "specialised"},
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
        keywords={"primary", "family"},
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
            f"{path}/clinic/primary.wav",
            f"{path}/care/specialist.wav",
            f"{path}/specialty/orthodontist.wav",
            f"{path}/form/remote.wav",
            f"{path}/date/tomorrow.wav",
        ],
    )

    print(whisper_sys.interpret())



    reference = "give me a specialist"
    hypothesis = "give me a special list"

    cer_val = cer(reference, hypothesis)
    wer_val = wer(reference, hypothesis)

    print(f"cer: {cer_val}\n"
          f"wer: {wer_val}")

