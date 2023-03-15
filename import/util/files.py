import soundfile

# check audio file if it is corrupted
def check_audio_file(filepath, expected_duration=1):
    try:
        with soundfile.SoundFile(filepath, "r") as f:
            frames = len(f)
            rate = f.samplerate
            duration = frames / float(rate)
            if duration < expected_duration:
                return True
            else:
                return False
    except Exception as e:
        print("File {} is corrupted with error: {}".format(filepath, str(e)))
        return False


# if run as script
if __name__ == "__main__":
    check_audio_file(
        "/net/z/Projekte/AMMOD/AudioData/BRITZ01/BRITZ01_202002/BRITZ01_200217_174500.wav"
    )
    check_audio_file(
        "/net/z/Projekte/AMMOD/AudioData/BRITZ01/BRITZ01_202001/BRITZ01_200103_013000.wav"
    )

