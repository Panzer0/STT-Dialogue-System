import whisper
import torch
import string


class WhisperClient:
    def __init__(self, model):
        torch.cuda.init()
        print("CUDA STATUS: ", torch.cuda.is_available())
        self.model = whisper.load_model(model).to("cuda")
        self.name = "Whisper"

    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        cleaned_text = text.translate(str.maketrans(punctuation, " " * len(punctuation))).lower()
        pruned_text = ' '.join(cleaned_text.split())
        return pruned_text

    def transcribe(self, audio: str) -> str:
        with torch.cuda.device("cuda"):
            return self.adjust_text(self.model.transcribe(audio)["text"])
