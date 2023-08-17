from collections import OrderedDict

import LinearDialogue
# todo: Rethink the below. Do I want to hard-code this, or read contents.json?
# CATEGORIES = OrderedDict([
#     ("clinic", {"primary", "secondary"}),
#     ("care", {"occupational", "primary", "specialist"}),
#     ("specialty"),
#     "form",
#     "date"])
# MISC_CHOICES = {"invalid.wav", }

if __name__ == '__main__':
    dial_system = LinearDialogue.generate()
    path = "audio/subjects/marcin"
    dial_system.run_files(
        [
            f"{path}/clinic/primary.wav",
            f"{path}/misc/invalid.wav",
            f"{path}/specialty/orthodontist.wav",
            f"{path}/form/remote.wav",
            f"{path}/date/tomorrow.wav",
        ],
    )

    print(dial_system.interpret())

    # reference = "give me a specialist"
    # hypothesis = "give me a special list"
    #
    # cer_val = cer(reference, hypothesis)
    # wer_val = wer(reference, hypothesis)
    #
    # print(f"cer: {cer_val}\n" f"wer: {wer_val}")
