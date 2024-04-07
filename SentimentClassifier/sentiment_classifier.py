from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


class FinancialSentimentAnalyzer:
    def __init__(self, model_path="path"):
        """
        Initializes the sentiment analyzer with the given model.
        :param model_path: The name of the model to load.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

    def predict_sentiment(self, text):
        """
        Predicts the sentiment of the given text.
        :param text: The text to analyze.
        :return: A string indicating the sentiment.
        """
        # Encode the text
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        # Predict
        with torch.no_grad():
            logits = self.model(**inputs).logits

        # Convert to probabilities
        probabilities = torch.softmax(logits, dim=1)
        sentiment_id = probabilities.argmax().item()

        # Map the sentiment ID to a string
        sentiment_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
        return sentiment_map.get(sentiment_id, "Unknown")
