import io
from pydub import AudioSegment
from pydub.effects import high_pass_filter
from enum import Enum


class SupportedFormat(str, Enum):
    RAW = "raw"
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"


def generate_snippet_buffer(
    file_path: str,
    target_format: SupportedFormat,
    start_ms: int,
    end_ms: int,
    audio_padding_ms: int = 5,
    high_pass_filter_frequency_hz: int = 0,
) -> io.BytesIO:
    """
    Loads the audio file from disk, extracts a snippet based on the provided start and end
    times (in milliseconds) with the given padding, applies optional high-pass filtering,
    converts it to the desired format (if applicable), and returns the audio snippet as an
    in-memory BytesIO buffer.

    Parameters:
      - file_path (str): The full path to the audio file.
      - target_format (SupportedFormat): The desired output format.
      - start_ms (int): Start time in milliseconds.
      - end_ms (int): End time in milliseconds.
      - audio_padding_ms (int): Additional padding in milliseconds to include before and after the snippet.
      - high_pass_filter_frequency_hz (int): Cutoff frequency in Hz for high-pass filter. 0 to disable.

    Returns:
      - io.BytesIO: Buffer containing the exported audio snippet.

    Raises:
      - Exception: If loading or exporting the audio fails.
    """
    try:
        # Convert any Decimal values to int/float to avoid type errors
        start_ms = float(start_ms)
        end_ms = float(end_ms)
        audio_padding_ms = float(audio_padding_ms)
        high_pass_filter_frequency_hz = float(high_pass_filter_frequency_hz)

        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        raise Exception(f"Error reading audio file: {e}")

    # Ensure snippet boundaries with padding.
    snippet = audio[
        max(0, start_ms - audio_padding_ms) : min(len(audio), end_ms + audio_padding_ms)
    ]

    # Apply high-pass filter if requested
    if high_pass_filter_frequency_hz > 0:
        snippet = high_pass_filter(snippet, high_pass_filter_frequency_hz)

    # Determine export format for conversion.
    if target_format == SupportedFormat.RAW:
        export_format = file_path.split(".")[-1]
    elif target_format == SupportedFormat.MP3:
        export_format = "mp3"
    elif target_format == SupportedFormat.WAV:
        export_format = "wav"
    elif target_format == SupportedFormat.FLAC:
        export_format = "flac"
    else:
        raise Exception(
            f"Invalid target format {target_format} Allowed values are: {SupportedFormat.RAW}, {SupportedFormat.MP3}, {SupportedFormat.WAV}, {SupportedFormat.FLAC}"
        )

    snippet_buffer = io.BytesIO()
    try:
        snippet.export(snippet_buffer, format=export_format)
    except Exception as e:
        raise Exception(f"Error exporting audio snippet: {e}")
    snippet_buffer.seek(0)
    return snippet_buffer


def save_snippet_to_file(
    file_path: str,
    target_path: str,
    target_format: SupportedFormat,
    start_ms: int,
    end_ms: int,
    audio_padding_ms: int = 5,
    high_pass_filter_frequency_hz: int = 0,
) -> str:
    """
    Extracts an audio snippet and saves it to the specified target path.

    Parameters:
      - file_path (str): The full path to the source audio file.
      - target_path (str): The full path where the snippet should be saved.
      - target_format (SupportedFormat): The desired output format.
      - start_ms (int): Start time in milliseconds.
      - end_ms (int): End time in milliseconds.
      - audio_padding_ms (int): Additional padding in milliseconds to include before and after the snippet.
      - high_pass_filter_frequency_hz (int): Cutoff frequency in Hz for high-pass filter. 0 to disable.

    Returns:
      - str: The path to the saved file.

    Raises:
      - Exception: If generating the snippet or writing to the target path fails.
    """
    try:
        # Generate the snippet buffer using the existing function
        snippet_buffer = generate_snippet_buffer(
            file_path=file_path,
            target_format=target_format,
            start_ms=start_ms,
            end_ms=end_ms,
            audio_padding_ms=audio_padding_ms,
            high_pass_filter_frequency_hz=high_pass_filter_frequency_hz,
        )

        # Write the buffer contents to the target file
        with open(target_path, "wb") as f:
            f.write(snippet_buffer.getvalue())

        return target_path
    except Exception as e:
        raise Exception(f"Error saving audio snippet to file: {e}")
