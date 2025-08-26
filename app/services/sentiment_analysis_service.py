from transformers import pipeline
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

# Load the sentiment-analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased")

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes sentiment of the given text using distilBERT model.
    :param text: Input text to analyze.
    :return: Sentiment score and label.
    """
    try:
        result = sentiment_analyzer(text)
        return result[0]  # Return the first result (the sentiment analysis output)
    except Exception as e:
        return {"error": str(e)}
