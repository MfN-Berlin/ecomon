import io
from pydub import AudioSegment

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
    padding_ms: int,
) -> io.BytesIO:
    """
    Loads the audio file from disk, extracts a snippet based on the provided start and end
    times (in milliseconds) with the given padding, converts it to the desired format (if applicable),
    and returns the audio snippet as an in-memory BytesIO buffer.

    Parameters:
      - file_path (str): The full path to the audio file.
      - original_ext (str): The original file extension (e.g. "wav", "mp3").
      - target_format (SupportedFormat): The desired output format.
      - start_ms (int): Start time in milliseconds.
      - end_ms (int): End time in milliseconds.
      - padding_ms (int): Additional padding in milliseconds to include before and after the snippet.

    Returns:
      - io.BytesIO: Buffer containing the exported audio snippet.

    Raises:
      - Exception: If loading or exporting the audio fails.
    """
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        raise Exception(f"Error reading audio file: {e}")

    # Ensure snippet boundaries with padding.
    snippet = audio[
        max(0, start_ms - padding_ms) : min(len(audio), end_ms + padding_ms)
    ]

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
            "Invalid target format. Allowed values are: 'raw', 'mp3', 'wav', 'flac'"
        )

    snippet_buffer = io.BytesIO()
    try:
        snippet.export(snippet_buffer, format=export_format)
    except Exception as e:
        raise Exception(f"Error exporting audio snippet: {e}")
    snippet_buffer.seek(0)
    return snippet_buffer
