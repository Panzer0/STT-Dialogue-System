import whisper
import torch
import string

from speechbrain.pretrained import EncoderDecoderASR


class SBClient:
    def __init__(self, model):
        self.model = EncoderDecoderASR.from_hparams(
            model, run_opts={"device": "cuda"}
        )

    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        cleaned_text = text.translate(str.maketrans(punctuation, " " * len(punctuation))).lower()
        pruned_text = ' '.join(cleaned_text.split())
        return pruned_text

    def transcribe(self, audio: str) -> str:
        return self.adjust_text(self.model.transcribe_file(audio))
