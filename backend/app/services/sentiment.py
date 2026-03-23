from datetime import datetime, timezone

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_text(text: str) -> dict:
    # if text is empty or whitespace, return neutral
    if not text or not text.strip():
        return {
            "score": 0.0,
            "label": "neutral",
            "emotion": "neutral",
            "analyzed_at": datetime.now(timezone.utc),
        }

    # analyze text using VADER
    scores = _analyzer.polarity_scores(text)

    # get the compound score (sentiment score)
    compound = scores["compound"]

    # label as postive, negative, or neutral
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {
        "score": compound,
        "label": label,
        "emotion": label,
        "analyzed_at": datetime.now(timezone.utc),
    }
