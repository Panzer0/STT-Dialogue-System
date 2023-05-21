from pydub import AudioSegment
import sys
import os
import scipy.io.wavefile

if __name__ == "__main__":
    # Set the filename variable to the value given as an argument
    file_name = sys.argv[1]

    # Split the file name into base name and extension
    base, ext = os.path.splitext(file_name)

    # Join the base name and the new extension
    new_name = base + ".wav"

    # Open the source file
    sound = AudioSegment.from_file(
        f"audio/misformatted/{file_name}", format=ext[1:]
    )

    # Save the .wav file
    sound.export(f"audio/wav/{new_name}", format="wav")

    # ## Doesn't work. Something seems to be wrong with my scipy installation
    # ## For the time being replace it with
    # ## `sox .\audio\wav\alright.wav -r 16000 .\audio\wav\alright2.wav`
    # # Load the .wav file
    # sample_rate, data = scipy.io.wavefile.read(f"audio/wav/{new_name}")
    #
    # # Change the sample rate
    # new_sample_rate = 16000
    #
    # # Save the .wav file with the new sample rate
    # scipy.io.wavefile.write(f"audio/wav/altered_{new_name}", new_sample_rate, data)
