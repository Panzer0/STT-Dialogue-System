import whisper
import torch
import string

from speechbrain.pretrained import EncoderDecoderASR



class SBClient():
    def __init__(self, model):
        self.model = EncoderDecoderASR.from_hparams(
            model, 
            run_opts={"device":"cuda"} 
        )

    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        return text.translate(str.maketrans("", "", punctuation)).lower()

    def transcribe(self, audio:str)->str:
        return self.adjust_text(self.model.transcribe_file(audio))
