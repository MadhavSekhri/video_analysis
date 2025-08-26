import requests
import json
from app.config.config import PERSPECTIVE_API_KEY
from app.config.config import MONGO_URI
from pymongo import MongoClient

def analyze_harmful_content(text: str) -> dict:
    """
    Analyzes harmful content using Perspective API.
    :param text: Input text to analyze.
    :return: Harmful content analysis result (e.g., hate speech, NSFW).
    """
    try:
        url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        params = {"key": PERSPECTIVE_API_KEY}
        data = {
            "comment": {"text": text},
            "languages": ["en"],
            "requestedAttributes": {
                "TOXICITY": {},
                "SEVERE_TOXICITY": {},
                "IDENTITY_ATTACK": {},
                "INSULT": {},
                "PROFANITY": {}
            }
        }

        response = requests.post(url, params=params, json=data)
        response.raise_for_status()  # Raise an error for HTTP issues
        analysis = response.json()

        # Validate that 'attributeScores' exists in the response
        if "attributeScores" not in analysis:
            return {"error": "attributeScores not found in the response"}

        # Extract useful data
        result = {
            "toxicity": analysis["attributeScores"]["TOXICITY"]["summaryScore"]["value"],
            "severe_toxicity": analysis["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"],
            "identity_attack": analysis["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"],
            "insult": analysis["attributeScores"]["INSULT"]["summaryScore"]["value"],
            "profanity": analysis["attributeScores"]["PROFANITY"]["summaryScore"]["value"]
        }
        return result

    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP error: {str(e)}"}
    except KeyError as e:
        return {"error": f"Missing key in response: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
