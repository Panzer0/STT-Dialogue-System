import whisper
import torch
import string
import torchaudio

from speechbrain.pretrained import EncoderDecoderASR
from speechbrain.utils.data_utils import split_path
from speechbrain.pretrained.fetching import fetch

class MyEncoderDecoderASR(EncoderDecoderASR):
    def load_audio(self, path, savedir="."):
        source, fl = split_path(path)
        path = fetch(fl, source=source, savedir=savedir, overwrite=True)
        signal, sr = torchaudio.load(str(path), channels_first=False)
        return self.audio_normalizer(signal, sr)



class SBClient:
    def __init__(self, model):
        self.model = MyEncoderDecoderASR.from_hparams(
            model, run_opts={"device": "cuda"}
        )
        self.name = "SpeechBrain"

    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        cleaned_text = text.translate(str.maketrans(punctuation, " " * len(punctuation))).lower()
        pruned_text = ' '.join(cleaned_text.split())
        return pruned_text

    def transcribe(self, audio: str) -> str:
        return self.adjust_text(self.model.transcribe_file(audio))
