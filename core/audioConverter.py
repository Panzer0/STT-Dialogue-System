from pydub import AudioSegment
import sys
import os
import glob

SUPPORTED_FORMATS = ["mp3", "ogg", "flac", "m4a", "aac"]


def convert_audio(input_path, output_path) -> None:
    sound = AudioSegment.from_file(input_path)
    sound.export(output_path, format="wav")


def convert_folder(input_folder, output_folder) -> None:
    os.makedirs(output_folder, exist_ok=True)

    audio_files = [
        file
        for ext in SUPPORTED_FORMATS
        for file in glob.glob(os.path.join(input_folder, f"*.{ext}"))
    ]

    for audio_file in audio_files:
        base_name = os.path.basename(audio_file)
        new_name = os.path.splitext(base_name)[0] + ".wav"
        output_path = os.path.join(output_folder, new_name)

        convert_audio(audio_file, output_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audioConverter.py input_folder output_folder")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        sys.exit(1)

    convert_folder(input_folder, output_folder)
