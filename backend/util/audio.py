import ffmpeg


def extract_part_from_audio_file_by_start_and_end_time(
    filepath,
    output_filepath,
    start_time,
    end_time,
    duration,
    padding=0,
    high_pass_frequency=0,
):
    stime = start_time - padding if (start_time - padding) > 0 else 0
    etime = end_time + padding if (end_time + padding) < duration else duration

    input = ffmpeg.input(
        filepath,
        ss=stime,
        to=etime,
        v="error",
    )
    audio = (
        input.audio.filter("highpass", f=high_pass_frequency)
        if high_pass_frequency > 0
        else input
    )
    ffmpeg.output(audio, output_filepath).run()
