import whisper
import torch

def speech_to_text(recording, model):
    val = torch.cuda.init()
    print("CUDA STATUS: ", torch.cuda.is_available())
    model = whisper.load_model(model).to("cuda")
    with torch.cuda.device("cuda"):
        return model.transcribe(recording)["text"]
