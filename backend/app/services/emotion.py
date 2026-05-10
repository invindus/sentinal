from datetime import datetime, timezone
from transformers import AutoTokenizer, AutoModelForSequenceClassification

task = 'sentiment'
MODEL = f"cardiffnlp/twitter-roberta-base-{task}"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.save_pretrained(MODEL)


def analyze_emotion(text: str) -> dict:
    """
    Analyze text emotions using RoBERTa model
    """

    if not text or not text.strip():
        return {
            "score": 0.0,
            "label": "neutral",
            "emotion": "neutral",
            "emotions": {},
            "analyzed_at": datetime.now(timezone.utc),
        }

    # Tokenization: splits text into tokens, converts tokens to IDs, formats tensors
    inputs = tokenizer(
        text,
        return_tensors = "pt",  # return PyTorch tensors
        truncation = True,      # cut off very long text since RoBERTa has a token limit ~512
        padding = True,         # ensure consistent tensor sizes for batching
        max_length = 512,
    )

    # Run inference (using a trained model to make predictions)
    with torch.no_grad(): # disables gradient tracking for less memory and faster inference
        outputs = model(**inputs)

    # Convert raw scores (logits) into probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim = -1)[0]

    # Map indexed outputs to readable emotions
    labels = model.config.id2label

    # Build emotion library
    emotion_scores = {
        labels[i]: float(probabilities[i]) for i in range(len(labels))
    }

    # Dominant emotion
    dominant_emotion = max(emotion_scores, key = emotion_scores.get)

    # Label overall sentiment
    positive_emotions = {"joy", "optimism", "love"}
    negative_emotions = {"anger", "sadness", "fear"}

    if dominant_emotion in positive_emotions:
        label = "positive"
    elif dominant_emotion in negative_emotions:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": emotion_scores[dominant_emotion],
        "label": label,
        "emotion": dominant_emotion,
        "emotions": emotion_scores,
        "analyzed_at": datetime.now(timezone.utc),
    }