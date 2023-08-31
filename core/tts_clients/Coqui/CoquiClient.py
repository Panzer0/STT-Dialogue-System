import argparse
import json
import shlex
import string
import subprocess
import sys
import wave
import numpy as np
from stt import Model, version
from timeit import default_timer as timer

try:
    from shlex import quote
except ImportError:
    from pipes import quote


class CoquiClient:
    def __init__(self, model, scorer="None"):
        self.model = Model(model)

        if scorer:
            self.model.enableExternalScorer(scorer)

    def convert_samplerate(self, audio_path, desired_sample_rate):
        sox_cmd = "sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - ".format(
            quote(audio_path), desired_sample_rate
        )
        try:
            output = subprocess.check_output(
                shlex.split(sox_cmd), stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "SoX returned non-zero status: {}".format(e.stderr)
            )
        except OSError as e:
            print(f"Audio path is {audio_path}")
            raise OSError(
                e.errno,
                "SoX not found, use {}hz files or install it: {}".format(
                    desired_sample_rate, e.strerror
                ),
            )

        return desired_sample_rate, np.frombuffer(output, np.int16)


    def adjust_text(self, text: str) -> str:
        punctuation = string.punctuation.replace("'", "")
        cleaned_text = text.translate(str.maketrans(punctuation, " " * len(punctuation))).lower()
        pruned_text = ' '.join(cleaned_text.split())
        return pruned_text

    def transcribe(self, audio: str) -> str:
        desired_sample_rate = self.model.sampleRate()

        fin = wave.open(audio, "rb")
        fs_orig = fin.getframerate()
        if fs_orig != desired_sample_rate:
            print(
                "Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.".format(
                    fs_orig, desired_sample_rate
                ),
                file=sys.stderr,
            )
            fs_new, audio = self.convert_samplerate(audio, desired_sample_rate)
        else:
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

        fin.close()

        return self.adjust_text(self.model.stt(audio))
