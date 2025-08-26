from fastapi import FastAPI
from app.routes import login, video_analysis_routes,audio_analysis_routes  # Import the video analysis routes

app = FastAPI()

# Include the login route in the application
app.include_router(login.router)
app.include_router(video_analysis_routes.router)
app.include_router(audio_analysis_routes.router)
