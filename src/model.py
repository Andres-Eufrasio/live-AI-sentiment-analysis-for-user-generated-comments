"""
Created by Andres Eufrasio Tinajero 
"""

import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification



class SentimentAnalysis:

    def __init__(self, model_name="unitary/toxic-bert", models_dir="./models"):
        self.models_dir = models_dir
        self.model_name = None
        self.path = None

        self.tokenizer = None
        self.model = None
        self.labels = None

        self.load_model(model_name)

    def validate_model_name(self, model_name: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)?", model_name):
            raise ValueError(f"Invalid model name: {model_name!r}")
        return model_name

    def load_model(self, model_name):
        """
        Load a Hugging Face sequence-classification model.

        If the model exists locally, load it from the local cache.
        Otherwise, download it from Hugging Face and cache it locally.
        """
        model_name = self.validate_model_name(model_name)

        self.shutdown_model()

        self.model_name = model_name
        self.path = os.path.join(self.models_dir, model_name)

        # Defense in depth: make sure the resolved path can't escape models_dir
        real_models_dir = os.path.realpath(self.models_dir)
        real_path = os.path.realpath(self.path)
        if os.path.commonpath([real_models_dir, real_path]) != real_models_dir:
            raise ValueError(f"Resolved path escapes models directory: {model_name!r}")

        os.makedirs(self.path, exist_ok=True)

        try:
            config_path = os.path.join(self.path, "config.json")

            if os.path.isfile(config_path):
                print(f"Loading local model: {model_name}")

                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.path,
                    local_files_only=True,
                )

                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.path,
                    local_files_only=True,
                )

            else:
                print(f"Downloading model: {model_name}")

                self.tokenizer = AutoTokenizer.from_pretrained(model_name)

                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name
                )

                # Cache locally
                self.tokenizer.save_pretrained(self.path)
                self.model.save_pretrained(self.path)

            self.labels = self.model.config.id2label
            self.model.eval()

            return True

        except Exception as ex:
            self.tokenizer = None
            self.model = None
            self.labels = None

            raise RuntimeError(
                f"Failed to load model '{model_name}': {ex}"
            ) from ex

    def switch_model(self, model_name) -> bool:
        """
        Hot-swap the currently active model.
        """
        if model_name == self.model_name and self.model is not None:
            return True

        print(f"Switching model: {self.model_name} -> {model_name}")

        return self.load_model(model_name)

    def shutdown_model(self):
        """
        Release the currently loaded model.
        """
        if self.model is not None:
            del self.model
            self.model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        self.labels = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def get_name(self):
        return self.model_name

    def get_labels(self):
        return self.labels

    def convert_to_json(self, prediction):

        probabilities = prediction.tolist()[0]

        return {
            label: probability
            for label, probability
            in zip(self.labels.values(), probabilities)
        }

    def predict(self, text, format=True):

        if self.model is None:
            raise RuntimeError("No model is currently loaded.")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        # Make sure inputs are on the same device as the model
        device = next(self.model.parameters()).device
        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            output = self.model(**inputs)

        probabilities = torch.softmax(
            output.logits,
            dim=1
        )

        if format:
            return self.convert_to_json(probabilities)

        return probabilities
            
        
        


if __name__ == "__main__":

    print("start")

    analyzer = SentimentAnalysis(
        "unitary/toxic-bert"
    )

    print(analyzer.predict("some text"))

    # HOT SWAP
    analyzer.switch_model(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )

    print(analyzer.predict("some text"))

    print(analyzer.get_name())
    print(analyzer.get_labels())





