"""
Created by Andres Eufrasio Tinajero 
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import torch


class SentimentAnalysis():

    def __init__(self, model = "", path = ""):

        self.name = "unitary/toxic-bert"
        self.path = "./models/"+self.name
        self.load_model()

        self.labels = self.model.config.id2label
        self.model.eval()

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


    def get_name(self):
        return self.name
    
    def get_labels(self) -> dict:  
        return self.labels

    def shutdown_model(self):
        try:
            del self.model
            torch.cuda.empty_cache()
            return True
        except Exception as e:
            raise RuntimeError(f"Model failed to shutdown: {e}")
        

    def convert_to_json(self, prediction):
        # [0] included because when tesnor is converted into a list it becomes a 2dArray with the contents in the first position.
        label_prediction = prediction.tolist()[0]
        json_prediction = {}
        
        for label,label_prediction in zip(self.labels.values(), label_prediction):
            json_prediction.update({label: label_prediction})
            
        return json_prediction

    def predict(self,text : str, format=True):
        #convert to pythorch tensors 
        input = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)

        with torch.no_grad():
            output = self.model(**input)

        logits = output.logits
        prediction = torch.softmax(logits, dim=1)
        if format == True:
            json_prediction = self.convert_to_json(prediction)
            return json_prediction
        else:
            return prediction
        
        


if __name__ == "__main__":
    start = SentimentAnalysis()
    print(start.predict("text"))
    print(start.labels)
    





