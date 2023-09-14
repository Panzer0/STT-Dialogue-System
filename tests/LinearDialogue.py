from jiwer import wer, cer

from core.dialogue.DialogueChoice import DialogueChoice
from core.dialogue.DialogueDate import DialogueDate
from core.dialogue.DialogueNode import DialogueNode
from core.dialogue.DialogueSystem import DialogueSystem
from core.tts_clients.Whisper.WhisperClient import WhisperClient


RETURN_KEYWORDS = {"return", "cancel", "back"}
JSON_PATH = "results.json"
RETURN_VAL = "-RETURN-"
DEFAULT_VAL = "-DEFAULT-"

# In this DialogueSystem, all choices lead to the same results.
def generate(client):
    # Dialogue system structure setup
    ## Date choice declarations
    date_valid_choice = DialogueDate(
        json_path=JSON_PATH,
        json_key="date",
    )
    date_return_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="date",
        json_value=RETURN_VAL,
        keywords=RETURN_KEYWORDS,
    )
    date_default_choice = DialogueChoice(
        json_path=JSON_PATH, json_key="date", json_value=DEFAULT_VAL
    )
    date_prompt = "When would you like to schedule the appointment for?"
    date_choices = {date_valid_choice, date_return_choice}
    date_node = DialogueNode(
        date_choices, default_choice=date_default_choice, prompt=date_prompt
    )

    ## Form choice declarations
    remote_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="form",
        json_value="remote",
        keywords={"remote", "remotely", "online", "virtual"},
        successor=date_node,
    )

    ## Form choice declarations
    personal_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="form",
        json_value="personal",
        keywords={"person", "personal", "personally"},
        successor=date_node,
    )
    form_return_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="form",
        json_value=RETURN_VAL,
        keywords=RETURN_KEYWORDS,
        successor=date_node,
    )
    form_default_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="form",
        json_value=DEFAULT_VAL,
        successor=date_node,
    )

    form_prompt = (
        "What form of appointment would you like to make?\n"
        "(Remote/in-person)"
    )
    form_choices = {remote_choice, personal_choice, form_return_choice}
    form_node = DialogueNode(
        form_choices, default_choice=form_default_choice, prompt=form_prompt
    )

    ## Specialist choice declarations
    orthodontist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value="orthodontist",
        keywords={"orthodontist", "dentist", "dentists", "teeth", "tooth"},
        successor=form_node,
    )
    oculist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value="oculist",
        keywords={"oculist", "oculists", "eye", "eyes"},
        successor=form_node,
    )
    psychiatrist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value="psychiatrist",
        keywords={"psychiatrist", "psychiatrists", "psychiatry", "mental"},
        successor=form_node,
    )
    cardiologist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value="cardiologist",
        keywords={
            "cardiologist",
            "cardiologists",
            "cardiology",
            "heart",
            "hearts",
        },
        successor=form_node,
    )
    laryngologist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value="laryngologist",
        keywords={"laryngologist", "laryngologists", "laryngology"},
        successor=form_node,
    )
    speciality_return_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value=RETURN_VAL,
        keywords=RETURN_KEYWORDS,
        successor=form_node,
    )
    specialty_default_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="specialty",
        json_value=DEFAULT_VAL,
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
        speciality_return_choice,
    }
    specialist_node = DialogueNode(
        specialist_choices,
        prompt=specialist_prompt,
        default_choice=specialty_default_choice,
    )

    ## Care choice declarations
    specialist_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="care",
        json_value="specialist",
        keywords={
            "specialist",
            "specialists",
            "special",
            "specialized",
            "specialised",
        },
        successor=specialist_node,
    )
    occupational_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="care",
        json_value="occupational",
        keywords={"occupational"},
        successor=specialist_node,
    )
    primary_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="care",
        json_value="primary",
        keywords={"primary", "family"},
        successor=specialist_node,
    )
    care_return_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="care",
        json_value=RETURN_VAL,
        keywords=RETURN_KEYWORDS,
        successor=specialist_node,
    )
    care_default_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="care",
        json_value=DEFAULT_VAL,
        successor=specialist_node,
    )
    care_prompt = (
        "What sort of physician would you like to make an appointment with?\n"
        "(Primary/special/occupational care)"
    )
    care_choices = {
        specialist_choice,
        occupational_choice,
        primary_choice,
        care_return_choice,
    }
    care_node = DialogueNode(
        care_choices, prompt=care_prompt, default_choice=care_default_choice
    )

    ## Clinic choice declarations
    primary_clinic_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="clinic",
        json_value="primary",
        keywords={"primary", "main", "park"},
        successor=care_node,
    )
    secondary_clinic_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="clinic",
        json_value="secondary",
        keywords={"secondary", "yellow"},
        successor=care_node,
    )
    clinic_return_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="clinic",
        json_value=RETURN_VAL,
        keywords=RETURN_KEYWORDS,
        successor=care_node,
    )
    clinic_default_choice = DialogueChoice(
        json_path=JSON_PATH,
        json_key="clinic",
        json_value=DEFAULT_VAL,
        successor=care_node,
    )
    clinic_prompt = (
        "Which clinic are you interested in?\n"
        "(Primary at Park Street / Secondary at Yellow Street)"
    )
    clinic_choices = {
        primary_clinic_choice,
        secondary_clinic_choice,
        clinic_return_choice,
    }
    clinic_node = DialogueNode(
        clinic_choices,
        default_choice=clinic_default_choice,
        prompt=clinic_prompt,
    )

    # Dialogue system setup
    dial_sys = DialogueSystem(JSON_PATH, clinic_node, client)
    return dial_sys
