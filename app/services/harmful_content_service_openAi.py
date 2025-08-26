import requests
import json
import openai
from app.config.config import WHISPER_API_KEY
from app.config.config import MONGO_URI
from pymongo import MongoClient

openai.api_key = WHISPER_API_KEY

def analyze_harmful_content(text: str) -> dict:
    """
    Analyze harmful content using OpenAI API.
    :param text: The input text to analyze.
    :return: A dictionary with the analysis results.
    """
    try:
        # Use GPT-3.5 Turbo for analysis
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that analyzes text for harmful content. Respond with a JSON object containing scores for 'toxicity', 'profanity', 'hate_speech', and 'insults'."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0
        )

        # Extract the response content
        analysis = response['choices'][0]['message']['content']
        return json.loads(analysis)

    except Exception as e:
        return {"error": str(e)}

# Test the function
text = "You're such an idiot! Nobody likes you."
result = analyze_harmful_content(text)
print(result)
