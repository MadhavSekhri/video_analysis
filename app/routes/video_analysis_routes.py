from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.models.analysis_model import VideoAnalysisResponse
from app.services.video_analysis_service import video_analysis
from app.utils.logger import log_message
import os
from app.services.video_analysis_service import analyze_segments_with_timestamps, generate_summary_with_timestamps
from app.services.audio_analysis_service import transcribe_audio_with_timestamps

from app.services.video_analysis_service import generate_summary_with_timestamps
from app.services.video_analysis_service import video_analysis
from app.services.audio_analysis_service import transcribe_audio
from app.services.sentiment_analysis_service import analyze_sentiment
from app.services.harmful_content_service import analyze_harmful_content

import time
from fastapi import HTTPException
from app.utils.logger import log_message
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.video_analysis_service import video_analysis
from app.services.video_analysis_service import detect_objects_and_scenes
from app.utils.jwt_utils import create_access_token
from app.utils.logger import log_message
from app.models.analysis_model import VideoAnalysisResponse
from pydantic import BaseModel
from app.utils.logger import log_message



router = APIRouter()


@router.post("/detect-objects", response_model=VideoAnalysisResponse)
async def detect_objects(file: UploadFile, output_dir: str = Form("./static/uploads")):
    """
    Endpoint to analyze video for object and scene detection.
    """
    try:
        # Save uploaded video
        video_path = os.path.join(output_dir, file.filename)
        with open(video_path, "wb") as f:
            f.write(await file.read())

        # Analyze the video
        result = detect_objects_and_scenes(video_path, output_dir)
        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/video-analysis")
async def analyze_video(file: UploadFile = File(...)):
    """
    Endpoint to analyze video, including transcript, sentiment analysis, and harmful content detection.
    """
    try:
        # Step 1: Save the uploaded video file
        upload_folder = "./static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        video_file_path = os.path.join(upload_folder, file.filename)
        
        with open(video_file_path, "wb") as f:
            f.write(await file.read())

        # Step 2: Perform video analysis
        analysis_summary = video_analysis(video_file_path)
        audio_file_url = analysis_summary["audio_file_url"]

        # Step 3: Perform audio transcription
        transcript = transcribe_audio(audio_file_url)
        if not transcript:
            raise HTTPException(status_code=500, detail="Audio transcription failed.")

        # Step 4: Perform sentiment analysis on the transcript
        sentiment_result = analyze_sentiment(transcript)

        # Step 5: Perform harmful content analysis on the transcript
        harmful_content_result = analyze_harmful_content(transcript)

        # Step 6: Prepare final response
        return JSONResponse(
            content={
                "metadata_id": analysis_summary["metadata_id"],
                "video_info": analysis_summary["video_info"],
                "audio_file_url": audio_file_url,
                "status": analysis_summary["status"],
                "message": analysis_summary["message"],
                "transcript": transcript,
                "sentiment_analysis": sentiment_result,
                "harmful_content_analysis": harmful_content_result,
                "excel_file_path": f"./static/uploads/{analysis_summary['metadata_id']}/{analysis_summary['metadata_id']}.xlsx"
            },
            status_code=200
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary/{metadata_id}")
async def generate_summary(metadata_id: str, audio: UploadFile = File(...)):
    """
    Generates a video analysis summary with timestamps based on transcript.
    """
    try:
        # Save audio file
        upload_folder = f"./static/uploads/{metadata_id}"
        os.makedirs(upload_folder, exist_ok=True)
        audio_file_path = os.path.join(upload_folder, audio.filename)
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(await audio.read())

        # Step 1: Transcribe audio with timestamps
        transcript_segments = transcribe_audio_with_timestamps(audio_file_path)
        if "error" in transcript_segments:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio.")

        # Step 2: Analyze transcript segments for problems
        detected_issues = analyze_segments_with_timestamps(transcript_segments)

        # Step 3: Generate summary file
        summary_file_path = generate_summary_with_timestamps(metadata_id, detected_issues, upload_folder)

        # Return response
        return {
            "metadata_id": metadata_id,
            "summary_file": summary_file_path,
            "issues_detected": detected_issues
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST route for video analysis
@router.post("/analyze-video", response_model=VideoAnalysisResponse)
async def analyze_video_endpoint(video: UploadFile = File(...)):
    try:
        # Validate the file extension
        valid_video_extensions = [".mp4", ".avi", ".mov"]
        if not any(video.filename.lower().endswith(ext) for ext in valid_video_extensions):
            log_message(f"Invalid video file format: {video.filename}", "ERROR")
            raise HTTPException(
                status_code=400, detail="Invalid video file format. Supported: .mp4, .avi, .mov"
            )
        if " " in video.filename:
            log_message(f"Invalid file name with spaces: {video.filename}", "ERROR")
            raise HTTPException(
                status_code=400, detail="File name contains spaces. Use a valid name."
            )

        # Save the file temporarily
        os.makedirs("static/uploads/video_files", exist_ok=True)
        video_file_path = f"static/uploads/video_files/{video.filename.replace(' ', '_')}"
        with open(video_file_path, "wb") as f:
            f.write(await video.read())

        log_message(f"File uploaded: {video.filename}")

        # Perform video analysis
        analysis_summary = video_analysis(video_file_path)

        # Clean up the uploaded file with retry logic
        # for _ in range(5):  # Retry up to 5 times
        #     try:
        #         os.remove(video_file_path)
        #         log_message(f"Analysis completed and file deleted: {video.filename}")
        #         break
        #     except PermissionError as e:
        #         log_message(f"File still in use, retrying: {video.filename}. Error: {str(e)}", "WARNING")
        #         time.sleep(1)  # Wait for 1 second before retrying
        #     except Exception as e:
        #         log_message(f"Unexpected error while deleting file: {video.filename}. Error: {str(e)}", "ERROR")
        #         break

        return analysis_summary

    except Exception as e:
        log_message(f"Error during video analysis: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
