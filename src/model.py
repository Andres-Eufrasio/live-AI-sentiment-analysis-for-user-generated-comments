"""
Created by Andres Eufrasio Tinajero 
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import torch


class SentimentAnalysis():

    def __init__(self, model_name="unitary/toxic-bert", models_dir="./models"):
        self.models_dir = models_dir
        self.model_name = model_name
        self.path = os.path.join(models_dir, model_name)

        self.tokenizer = None
        self.model = None
        self.labels = None

        self.load_model(model_name)

    def load_model(self):
        try:
            if os.path.exists(self.path):
                self.tokenizer = AutoTokenizer.from_pretrained(self.path)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.path)
            else:
                os.makedirs(self.path, exist_ok=True)
                self.tokenizer = AutoTokenizer.from_pretrained(self.name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.name)

                #SAVE locally 
                self.tokenizer.save_pretrained(self.path)
                self.model.save_pretrained(self.path)
        except Exception as ex:
            print(f"failed to load model {ex}")


    def load_model(self, model_name):
            """
            Load a Hugging Face model. If it exists locally, use the
            local copy; otherwise download it and cache it.
            """

            # Unload the currently active model first
            self.shutdown_model()

            self.model_name = model_name
            self.path = os.path.join(self.models_dir, model_name)

            os.makedirs(self.path, exist_ok=True)

            try:
                if os.path.exists(os.path.join(self.path, "config.json")):
                    print(f"Loading local model: {model_name}")

                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.path
                    )

                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        self.path
                    )

                else:
                    print(f"Downloading model: {model_name}")

                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name
                    )

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
                )

    def switch_model(self, model_name):
        """
        Hot-swap the currently active model.
        """

        if model_name == self.model_name and self.model is not None:
            return

        print(f"Switching model: {self.model_name} -> {model_name}")

        self.load_model(model_name)

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
    start = SentimentAnalysis()
    print(start.predict("text"))
    print(start.labels)
    





