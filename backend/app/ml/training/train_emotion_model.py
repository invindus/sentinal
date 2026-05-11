from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
)
from sklearn.metrics import f1_score

import numpy as np
import torch

# ---------------- HELPER FUNCTIONS ----------------


def tokenize(example):
    return tokenizer(
        example["text"],
        return_tensors="pt",  # return PyTorch tensors
        truncation=True,  # cut off very long text since RoBERTa has a token limit ~512
        padding=True,  # ensure consistent tensor sizes for batching
        max_length=128,
    )


def encode_labels(example):
    """
    GoEmotion labels look like [3, 11].
    Need to convert into [0,0,0,1,0,0,...,1,...]
    """
    label_vector = np.zeros(num_labels)

    for label in example["labels"]:
        label_vector[label] = 1

    example["labels"] = label_vector.to_list()

    return example


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = torch.sigmoid(torch.tensor(logits)).numpy()
    preds = (probs > 0.5).astype(int)

    f1 = f1_score(labels, preds, average="micro")
    return {
        "micro_f1": f1,
    }


# ---------------- END HELPER FUNCTIONS ----------------

# 1. Load dataset
dataset = load_dataset("go_emotions")
labels = dataset["train"].features["labels"].feature.names
num_labels = len(labels)

# 2. Load tokenizer
MODEL_NAME = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
dataset = dataset.map(tokenize)

# 3. Encode labels
dataset = dataset.map(encode_labels)

# 4. Format for PyTorch
dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "labels"],
)

# 5. Load model for multi-label classification
# Problem Type changes loss function, output interpretation,
# # and training behaviour for classification
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=num_labels, problem_type="multi_label_classification"
)

# 6. Metrics
# 7. Training Configuration
