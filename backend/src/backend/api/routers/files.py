from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from fastapi.responses import StreamingResponse
import os
import io
import re
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    target_format: TargetFormat = TargetFormat.RAW,
    padding_ms: int = Query(
        0,
        ge=0,
        description="Padding in milliseconds to include before and after the snippet",
    ),
):
    """
    Retrieve an audio snippet from a record based on the exact start and end times
    of an inference result, with an optional format transformation and support for
    HTTP Range requests to allow seeking.

    The endpoint supports an optional path parameter 'target_format' which can be:
      - "raw": serve the snippet in its original format.
      - "mp3": convert the snippet to MP3.
      - "wav": convert the snippet to WAV.
      - "flac": convert the snippet to FLAC (a lossless format).

    Additionally, if a Range header is provided in the request,
    a partial content (206) response is sent with the appropriate Content-Range.

    Query Parameters:
      - padding_ms: Padding around the snippet in milliseconds (default is 5000ms).
    """
    # Query the record entry.
    result = await db.execute(select(Records).filter(Records.id == record_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    # Query the inference result, ensuring it belongs to this record.
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
    snippet_audio = audio[
        max(0, start_ms - padding_ms) : min(len(audio), end_ms + padding_ms)
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

    # Get the full content from the buffer.
    content = snippet_buffer.getvalue()
    file_size = len(content)

    # Check for a Range header to support partial content for seeking.
    range_header = request.headers.get("range")
    if range_header:
        range_match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end_str = range_match.group(2)
            end = int(end_str) if end_str != "" else file_size - 1

            # Ensure the range is satisfiable.
            if start >= file_size:
                raise HTTPException(
                    status_code=416, detail="Requested Range Not Satisfiable"
                )
            if end >= file_size:
                end = file_size - 1

            partial_content = content[start : end + 1]
            partial_headers = {
                "Content-Disposition": f"attachment; filename={final_filename}",
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(partial_content)),
            }
            return Response(
                content=partial_content,
                status_code=206,
                media_type=media_type,
                headers=partial_headers,
            )

    # If no Range header is provided, send the full content.
    full_headers = {
        "Content-Disposition": f"attachment; filename={final_filename}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
    }
    return StreamingResponse(
        io.BytesIO(content), media_type=media_type, headers=full_headers
    )
