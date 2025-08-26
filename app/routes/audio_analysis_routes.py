from fastapi import APIRouter, HTTPException, File, UploadFile
from app.services.audio_analysis_service import transcribe_audio
from app.services.sentiment_analysis_service import analyze_sentiment
from app.services.harmful_content_service import analyze_harmful_content
from fastapi.responses import JSONResponse
import os

router = APIRouter()

@router.post("/audio-analysis/{metadata_id}")
async def analyze_audio(metadata_id: str, file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        upload_folder = f"./static/uploads/{metadata_id}"
        os.makedirs(upload_folder, exist_ok=True)
        audio_file_path = os.path.join(upload_folder, f"{metadata_id}.mp3")
        
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(await file.read())
        
        # Transcribe audio to text
        transcription = transcribe_audio(audio_file_path)
        if not transcription:
            raise HTTPException(status_code=500, detail="Audio transcription failed.")
        
        # Sentiment analysis
        sentiment_result = analyze_sentiment(transcription)
        
        # Harmful content analysis
        harmful_content_result = analyze_harmful_content(transcription)

        # Combine results
        response = {
            "metadata_id": metadata_id,
            "transcription": transcription,
            "sentiment_score": sentiment_result,
            "harmful_content_flags": harmful_content_result
        }

        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
