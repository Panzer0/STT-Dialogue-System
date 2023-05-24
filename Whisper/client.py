import whisper

def speech_to_text(recording, model):
    model = whisper.load_model(model)
    return model.transcribe(recording)["text"]
