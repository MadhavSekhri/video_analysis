import os
import subprocess
import shlex
import ffmpeg
import random
import cv2
from fastapi import HTTPException
from app.services.sentiment_analysis_service import analyze_sentiment
from app.services.harmful_content_service import analyze_harmful_content

from app.utils.logger import log_message
import datetime
from app.models.analysis_model import VideoAnalysisResponse

from app.utils.mongo_utils import MongoDB
import time
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the base upload folder exists


def generate_metadata_id():
    """
    Generate a unique metadata ID using the current timestamp and a random number.
    """
    timestamp = int(time.time())  # Current time in seconds since epoch
    random_number = random.randint(1000, 9999)  # A random 4-digit number
    metadata_id = f"{timestamp}{random_number}"  # Combine timestamp and random number
    return metadata_id


def create_metadata_folder(metadata_id):
    """
    Create a directory for storing files related to the metadata ID.
    """
    # Format the current timestamp for readability
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # folder_name = f"{metadata_id}_{timestamp}"
    folder_name = f"{metadata_id}"

    # Full folder path
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Ensure the folder is created
    return folder_path


def video_analysis(video_file_path: str) -> dict:
    if not os.path.exists(video_file_path):
        log_message(f"Error: Video file {video_file_path} does not exist.", "ERROR")
        raise HTTPException(status_code=400, detail="Video file not found.")

    # Generate metadata ID and create the storage folder
    metadata_id = generate_metadata_id()
    metadata_folder = create_metadata_folder(metadata_id)

    # Rename and move video file to the metadata folder
    video_file_name = f"{metadata_id}.mp4"
    renamed_video_path = os.path.join(metadata_folder, video_file_name)
    os.rename(video_file_path, renamed_video_path)

    # Extract audio and save it in the same folder
    audio_file_name = f"{metadata_id}.mp3"
    audio_file_path = os.path.join(metadata_folder, audio_file_name)
    audio_file_url = extract_audio_from_video(renamed_video_path, audio_file_path)

    # Process video metadata
    video_info = process_video(renamed_video_path, metadata_folder)

    # Save an example Excel file in the same folder (optional)
    excel_file_name = f"{metadata_id}.xlsx"
    excel_file_path = os.path.join(metadata_folder, excel_file_name)
    save_metadata_to_excel(metadata_id, video_info, excel_file_path)

    # Insert metadata into MongoDB
    metadata = {
        "metadataId":metadata_id,
        "video_file_path": video_file_path,
        "audio_file_url": audio_file_url,
        "video_info": video_info,
        "status": "pending",
        "uploadTimestamp": datetime.datetime.now().isoformat(),
        "processedTimestamp":""
    }

    try:
        mongo_db = MongoDB()  # Create an instance of MongoDB
        inserted_id = mongo_db.insert_document('videoMetadata', metadata)  # Insert into MongoDB
        log_message(f"Video metadata inserted with ID: {inserted_id}")
    except Exception as e:
        log_message(f"Error inserting metadata into MongoDB: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail="Failed to insert metadata into MongoDB.")

    # Return the response
    return {
        "metadata_id": metadata_id,
        "folder_name": metadata_folder,
        "video_info": video_info,
        "audio_file_url": audio_file_url,
        "status": "success",
        "message": "Video analysis completed successfully",
    }


def process_video(video_file_path: str, folder_name: str) -> dict:
    """
    Extract video metadata and return it as a dictionary.
    """
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        log_message(f"Error: Unable to open video file {video_file_path}", "ERROR")
        raise HTTPException(status_code=500, detail="Video processing failed.")

    # Extract metadata
    width = int(    (cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration_seconds = frame_count / fps if fps else 0
    duration_minutes = round(duration_seconds / 60, 2) if duration_seconds else 0
    fps = round(fps, 2)  # Round FPS to 2 decimal places

    # Release the video capture object
    cap.release()

    video_info = {
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "fps": fps,
        "duration_minutes": duration_minutes,  # Changed to duration in minutes
    }
    log_message(f"Video processed successfully: {video_info}")
    return video_info


def extract_audio_from_video(video_file_path: str, audio_file_path: str) -> str:
    """
    Extract audio from the video file and save it as an MP3.
    """
    try:
        ffmpeg_command = f"ffmpeg -i {shlex.quote(video_file_path)} -vn -acodec mp3 {shlex.quote(audio_file_path)}"
        subprocess.run(shlex.split(ffmpeg_command), check=True)
        log_message(f"Audio extracted successfully: {audio_file_path}")
        return audio_file_path
    except subprocess.CalledProcessError as e:
        log_message(f"Error extracting audio from video: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail="Failed to extract audio from video.")

def detect_objects_and_scenes(video_path: str, output_dir: str) -> dict:
    """
    Detect objects and scenes in a video using YOLOv8.
    :param video_path: Path to the input video file (.mp4).
    :param output_dir: Path to save the processed frames and results.
    :return: A dictionary with timestamps and detected objects/scenes.
    """
    try:
        # Load the YOLOv8 model
        model = YOLO("yolov8n.pt")

        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file!")

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Get frames per second
        results = []  # Store detection results
        frame_count = 0

        # Process the video frame by frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            frame_count += 1
            timestamp = frame_count / frame_rate

            # Analyze every Nth frame (e.g., every 5th frame to save processing time)
            if frame_count % 5 == 0:
                detections = model.predict(frame, conf=0.5)  # Run YOLOv8 detection
                result = {
                    "timestamp": round(timestamp, 2),  # Timestamp in seconds
                    "detections": detections[0].names,  # Detected objects
                }
                results.append(result)

                # Optional: Save processed frames with detections as images
                for detection in detections[0].boxes:
                    x1, y1, x2, y2 = map(int, detection.xyxy)
                    label = detection.name
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                output_frame_path = f"{output_dir}/frame_{frame_count}.jpg"
                cv2.imwrite(output_frame_path, frame)  # Save frame

        cap.release()

        return {
            "status": "success",
            "message": "Video analyzed successfully",
            "detections": results
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_segments_with_timestamps(transcript_segments: list) -> list:
    """
    Analyzes transcript segments for harmful content and sentiment.
    :param transcript_segments: List of segments with text and timestamps.
    :return: List of issues detected with timestamps.
    """
    detected_issues = []

    for segment in transcript_segments:
        start_time = segment['start']
        text = segment['text']

        # Analyze for harmful content
        harmful_content_result = analyze_harmful_content(text)
        if harmful_content_result.get('toxicity_score', 0) > 0.5:  # Threshold for toxicity
            detected_issues.append({
                "timestamp": format_timestamp(start_time),
                "problem": "Toxic content detected"
            })

        # Analyze for sentiment
        sentiment_result = analyze_sentiment(text)
        if sentiment_result.get('label') == "NEGATIVE":
            detected_issues.append({
                "timestamp": format_timestamp(start_time),
                "problem": "Negative sentiment detected"
            })

    return detected_issues

def format_timestamp(seconds: float) -> str:
    """
    Formats time in seconds to HH:MM:SS.
    """
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{sec:02}"



def generate_summary_with_timestamps(metadata_id: str, video_issues: list, folder_path: str) -> str:
    """
    Generate a summary file with timestamps and detected problems.
    :param metadata_id: Unique ID for the video analysis.
    :param video_issues: List of dictionaries with 'timestamp' and 'problem' keys.
    :param folder_path: Path to the folder where the summary file will be stored.
    :return: Path to the summary file.
    """
    try:
        # Create a summary .txt file
        summary_file_path = os.path.join(folder_path, f"{metadata_id}_summary.txt")
        with open(summary_file_path, "w") as summary_file:
            summary_file.write("Video Analysis Summary:\n\n")
            for issue in video_issues:
                summary_file.write(f"{issue['problem']} at {issue['timestamp']}\n")
        return summary_file_path
    except Exception as e:
        raise Exception(f"Error generating summary file: {str(e)}")


def save_metadata_to_excel(metadata_id, video_info, excel_file_path):
    """
    Save metadata information to an Excel file.
    """
    try:
        import pandas as pd

        # Example: Create a DataFrame and write it to Excel
        data = {
            "Metadata ID": [metadata_id],
            "Width": [video_info["width"]],
            "Height": [video_info["height"]],
            "Frame Count": [video_info["frame_count"]],
            "FPS": [video_info["fps"]],
        }
        df = pd.DataFrame(data)
        df.to_excel(excel_file_path, index=False)
        log_message(f"Metadata saved to Excel: {excel_file_path}")
    except Exception as e:
        log_message(f"Error saving metadata to Excel: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail="Failed to save metadata to Excel.")
