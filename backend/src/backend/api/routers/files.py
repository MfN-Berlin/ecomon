from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import os
import io
from pydub import AudioSegment

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import your database dependency and models
from backend.api.database import get_db
from backend.shared.models.db.models import Records, ModelInferenceResults

# Import ApiSettings to get the base data directory for files
from backend.api.settings import ApiSettings

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/records/{record_id}/inference-result/{result_id}")
async def get_record_inference_result(
    record_id: int, result_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve an audio snippet from a record based on the exact start and end times
    of an inference result. The file is loaded from disk using the record file's path,
    trimmed according to the times indicated in ModelInferenceResults (in seconds),
    and streamed back as a file with its original MIME type and filename.
    """
    # Check if the record exists
    result = await db.execute(select(Records).filter(Records.id == record_id))
    record = result.scalars().first()
    padding = 5000
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    # Check if the inference result exists and is linked to the record.
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

    # Build the full file path by combining the base data directory and the record's file path.
    settings = ApiSettings()
    file_path = os.path.join(settings.base_data_directory, record.filepath)
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
        )

    # Load the audio file (assuming it is in WAV format)
    try:
        audio = AudioSegment.from_file(file_path, format="wav")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading audio file: {e}",
        )

    # Convert start and end times from seconds to milliseconds
    start_ms = int(inference_result.start_time * 1000)
    end_ms = int(inference_result.end_time * 1000)
    if end_ms <= start_ms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid snippet times: end_time must be greater than start_time",
        )

    # Extract the snippet from the audio file
    base_filename = record.filename.split(".")[0]
    extension = record.filename.split(".")[1]
    snippet_audio = audio[
        max(0, start_ms - padding) : min(len(audio), end_ms + padding)
    ]

    # Export the snippet to an in-memory byte stream (BytesIO)
    snippet_buffer = io.BytesIO()
    snippet_audio.export(snippet_buffer, format=extension)
    snippet_buffer.seek(0)

    # Use the media type and filename from the record entry

    headers = {
        "Content-Disposition": f"attachment; filename={base_filename}_{inference_result.start_time}_{inference_result.end_time}.{extension}"
    }
    return StreamingResponse(
        snippet_buffer, media_type=record.mime_type, headers=headers
    )
