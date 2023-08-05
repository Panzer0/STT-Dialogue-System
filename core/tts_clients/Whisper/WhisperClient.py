import whisper
import torch
import string



class WhisperClient:
    def __init__(self, model):
        torch.cuda.init()
        print("CUDA STATUS: ", torch.cuda.is_available())
        self.model = whisper.load_model(model).to("cuda")

        
    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        return text.translate(str.maketrans("", "", punctuation)).lower()

    def transcribe(self, audio: str) -> str:
        with torch.cuda.device("cuda"):
            # Skipping last symbol because it's always '.'
            return self.adjust_text(self.model.transcribe(audio)["text"])
