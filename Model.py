"""
Created by Andres 02 may 2026

To do: pick one specific model for it to load
allow for local models
interaction with the api
continous loop for interaction
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

Sentiment_model = "unitary/toxic-bert"

#Download toxic bert
tokenizer = AutoTokenizer.from_pretrained(Sentiment_model)
model= AutoModelForSequenceClassification.from_pretrained(Sentiment_model)

#switch to inference model for predicting without training
model.eval()

test_text = "fuck off mom"

#convert to pythorch tensors 
input = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)

#don't track gradient since I'm not doing training
with torch.no_grad():
    output = model(**input)


logits = output.logits
#reduce dementionality to get final results 
probs = torch.softmax(logits, dim=1)


#toxic, severe_toxic, obscene, threat, insult, and identity_hate
print("Logits:", logits)
print("Probabilities:", probs)

