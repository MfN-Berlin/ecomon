from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import os
import io
from pydub import AudioSegment
from enum import Enum

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import your database dependency and models
from backend.api.database import get_db
from backend.shared.models.db.models import Records, ModelInferenceResults

# Import ApiSettings to get the base data directory for files
from backend.api.settings import ApiSettings

router = APIRouter(prefix="/files", tags=["files"])


class TargetFormat(str, Enum):
    RAW = "raw"
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"


@router.get(
    "/records/{record_id}/inference-result/{result_id}",
    response_class=StreamingResponse,
)
@router.get(
    "/records/{record_id}/inference-result/{result_id}/{target_format}",
    response_class=StreamingResponse,
)
async def get_record_inference_result(
    record_id: int,
    result_id: int,
    db: AsyncSession = Depends(get_db),
    target_format: TargetFormat = TargetFormat.RAW,
):
    """
    Retrieve an audio snippet from a record based on the exact start and end times
    of an inference result, with an optional format transformation.

    The endpoint supports an optional path parameter 'target_format' which can be:
      - "raw": serve the snippet in its original format.
      - "mp3": convert the snippet to MP3.
      - "wav": convert the snippet to WAV.
      - "flac": convert the snippet to FLAC (a lossless format).

    The audio file is loaded from disk using its stored filepath, trimmed (with optional padding),
    and then exported (optionally converting its format). The response headers use the media type
    and filename read from the record—updated if a conversion takes place.
    """
    # Query the record entry
    result = await db.execute(select(Records).filter(Records.id == record_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    # Query the inference result, ensuring it belongs to this record
    result = await db.execute(
        select(ModelInferenceResults).filter(
            ModelInferenceResults.id == result_id,
            ModelInferenceResults.record_id == record_id,
        )
    )
    inference_result = result.scalars().first()
    if not inference_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inference result not found for this record",
        )

    # Build the full file path using the base data directory and the record's filepath.
    settings = ApiSettings()
    file_path = os.path.join(settings.base_data_directory, record.filepath)
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
        )

    # Determine the original file extension.
    if "." in record.filename:
        original_ext = record.filename.rsplit(".", 1)[-1].lower()
    else:
        original_ext = "wav"  # default if none found

    # Load the audio file using pydub.
    try:
        audio = AudioSegment.from_file(file_path, format=original_ext)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading audio file: {e}",
        )

    # Convert start and end times from seconds to milliseconds.
    start_ms = int(inference_result.start_time * 1000)
    end_ms = int(inference_result.end_time * 1000)
    if end_ms <= start_ms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid snippet times: end_time must be greater than start_time",
        )

    # (Optional) Add padding (in milliseconds) around the snippet.
    padding = 5000
    snippet_audio = audio[
        max(0, start_ms - padding) : min(len(audio), end_ms + padding)
    ]

    # Determine if a conversion is requested based on the TargetFormat type.
    if target_format == TargetFormat.RAW:
        export_format = original_ext
        media_type = record.mime_type
        file_extension = original_ext
    elif target_format == TargetFormat.MP3:
        export_format = "mp3"
        media_type = "audio/mpeg"
        file_extension = "mp3"
    elif target_format == TargetFormat.WAV:
        export_format = "wav"
        media_type = "audio/wav"
        file_extension = "wav"
    elif target_format == TargetFormat.FLAC:
        export_format = "flac"
        media_type = "audio/flac"
        file_extension = "flac"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target format. Allowed values are: 'raw', 'mp3', 'wav', 'flac'",
        )

    # Export the snippet to an in-memory buffer in the desired format.
    snippet_buffer = io.BytesIO()
    try:
        snippet_audio.export(snippet_buffer, format=export_format)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting audio snippet: {e}",
        )
    snippet_buffer.seek(0)

    # Construct a filename for the exported snippet.
    base_filename = record.filename.rsplit(".", 1)[0]
    final_filename = f"{base_filename}_{inference_result.start_time}_{inference_result.end_time}.{file_extension}"

    headers = {"Content-Disposition": f"attachment; filename={final_filename}"}
    return StreamingResponse(snippet_buffer, media_type=media_type, headers=headers)
