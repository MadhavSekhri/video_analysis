import whisper
from pydub import AudioSegment
import os
import warnings
from tqdm import tqdm

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU")
# app/services/audio_analysis_service.py

from pydub import AudioSegment
import os
import whisper

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file (MP3) to text using the Whisper model from OpenAI,
    running locally without the need for an API key.
    :param audio_path: Path to the MP3 file.
    :return: The transcribed text from the audio file.
    """
    try:
        # Convert MP3 to WAV using pydub
        audio = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")

        # Load the Whisper model
        model = whisper.load_model("base")

        # Transcribe the audio file
        result = model.transcribe(wav_path)

        # Clean up the temporary WAV file
        os.remove(wav_path)

        return result.get("text", "Error: No text returned from transcription.")
    
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return f"Error: {e}"


def transcribe_audio_with_timestamps(audio_path: str) -> list:
    """
    Transcribes an audio file and returns text segments with timestamps.
    :param audio_path: Path to the MP3 file.
    :return: List of segments with text and timestamps.
    """
    try:
        # Convert audio to WAV
        audio = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")

        # Load Whisper model and transcribe
        model = whisper.load_model("base")
        result = model.transcribe(wav_path, word_timestamps=True)

        # Clean up the temporary WAV file
        os.remove(wav_path)

        # Return segments with timestamps
        segments = []
        for segment in result['segments']:
            segments.append({
                "start": segment['start'],  # Start time in seconds
                "end": segment['end'],      # End time in seconds
                "text": segment['text']     # Text content
            })
        return segments
    except Exception as e:
        return {"error": str(e)}

# def transcribe_audio_with_progress(audio_path: str) -> str:
#     """
#     Transcribes an audio file (MP3) to text using the Whisper model from OpenAI,
#     running locally without the need for an API key. Adds a progress tracker for large files.
#     Converts MP3 to WAV format before sending to the model.
#     :param audio_path: Path to the MP3 file.
#     :return: The transcribed text from the audio file.
#     """
#     try:
#         # Convert MP3 to WAV using pydub
#         audio = AudioSegment.from_mp3(audio_path)
#         wav_path = audio_path.replace(".mp3", ".wav")
#         audio.export(wav_path, format="wav")

#         # Load the Whisper model
#         model = whisper.load_model("base")  # You can use "small", "medium", or "large" for higher accuracy

#         # Split the audio into smaller chunks (e.g., 30-second chunks) to process with progress
#         chunk_duration_ms = 30000  # 30 seconds
#         total_duration_ms = len(audio)
#         num_chunks = total_duration_ms // chunk_duration_ms + (1 if total_duration_ms % chunk_duration_ms > 0 else 0)

#         # Create a progress bar using tqdm
#         progress_bar = tqdm(total=num_chunks, desc="Transcribing Audio", unit="chunk")

#         transcribed_text = ""
        
#         for i in range(num_chunks):
#             start_ms = i * chunk_duration_ms
#             end_ms = min((i + 1) * chunk_duration_ms, total_duration_ms)
#             chunk = audio[start_ms:end_ms]

#             # Save the chunk as a temporary WAV file
#             chunk_wav_path = f"{wav_path}_chunk_{i}.wav"
#             chunk.export(chunk_wav_path, format="wav")

#             # Transcribe the chunk
#             result = model.transcribe(chunk_wav_path)
#             transcribed_text += result.get("text", "") + " "

#             # Remove the temporary chunk file
#             os.remove(chunk_wav_path)

#             # Update the progress bar
#             progress_bar.update(1)

#         # Close the progress bar
#         progress_bar.close()

#         # Clean up the original WAV file
#         os.remove(wav_path)

#         # Return the transcribed text
#         if transcribed_text:
#             return transcribed_text.strip()
#         else:
#             return "Error: No text returned from transcription."

#     except Exception as e:
#         print(f"Error during audio transcription: {e}")
#         return f"Error: {e}"



# Example usage
# audio_file_path = "C:/Users/Madhav Sekhri/Downloads/oh-my-love-247222.mp3"
# transcription = transcribe_audio_with_progress(audio_file_path)
# print(transcription)
