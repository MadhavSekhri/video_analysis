from pydantic import BaseModel
from pydantic import BaseModel
from typing import List, Dict

class VideoInfo(BaseModel):
    timestamp: float
    detections: List[str]

class VideoAnalysisResponse(BaseModel):
    video_info: dict  # Information about the video
    audio_file_url: str  # URL of the extracted audio file
    status: str  # Status of the video analysis
    message: str  # Any relevant message related to the analysis result

    class Config:
        orm_mode = True
