from celery import Celery
import base64
import uuid
import yaml
from sentiment_classifier import FinancialSentimentAnalyzer

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "sentimentclassifier",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="classify_sentiment")
def classify_sentiment(text):
    analyzer = FinancialSentimentAnalyzer("model")
    sentiment = analyzer.predict_sentiment(text)
    print(f"Sentiment: {sentiment}")
    return sentiment
