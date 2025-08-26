import json
from transformers import pipeline

def analyze_harmful_content(text: str) -> dict:
    """
    Analyze harmful content using Hugging Face Transformers.
    :param text: The input text to analyze.
    :return: A dictionary with the analysis results.
    """
    try:
        # Load the toxicity analysis model from Hugging Face
        toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert")

        # Use the model to predict the toxicity of the text
        analysis = toxicity_pipeline(text)
        # hate_speech_pipeline = pipeline("text-classification", model="facebook/roberta-hate-speech-detection")
        # profanity_pipeline = pipeline("text-classification", model="microsoft/DialoGPT-medium")  # Adjust with an actual profanity model if available

        # Extract the result and return in a structured format
        result = {
            "toxicity_score": analysis[0]['score'],
            "label": "toxicity"
        }

        # You can add additional fields like profanity, hate speech, etc., if your model supports them
        # For now, we assume the model returns toxicity score and label.
        return result

    except Exception as e:
        return {"error": str(e)}

# Test the function
text = "I got new job."
result = analyze_harmful_content(text)
print(result)
    