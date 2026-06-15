"""
Created by Andres Eufrasio Tinajero 
may 2nd 2026

To do: pick one specific model for it to load
allow for local models
interaction with the api
continous loop for interaction
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from fastapi import FastAPI

"""
A sentiement analysis predictor that loads a huging face model
Precondition:
Comment text

Postcondition:
json with labels and probability
"""
class HFSentimentAnalysis():

    def __init__(self):

        self.name = "unitary/toxic-bert"
        self.path = "./models/"
        try:   
            self.tokenizer = AutoTokenizer.from_pretrained(self.name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.name)
        except Exception as ex:
            print(f"failed to load model {ex}")
        self.labels = self.model.config.id2label
        self.model.eval()

    def get_name(self):
        return self.name
    
    def shutdown_model(self):
        del self.model
        torch.cuda.empty_cache()
        
    def convert_to_json(self, prediction):
        # [0] included because when tesnor is converted into a list it becomes a 2dArray with the contents in the first position.
        label_prediction = prediction.tolist()[0]
        json_prediction = {}
        print(label_prediction)
        
        for label,label_prediction in zip(self.labels.values(), label_prediction):
            json_prediction.update({label: label_prediction})
            
        print(json_prediction)
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
        
    def downlaod(self):
        self.model.download()
            
"""
class PredictionSystem():
    pass
app = FastAPI()
model = False
@app.get("/")
def load_model():
    model = HFSentimentAnalysis()
    if model != False:
        return {"Status": "is now running"}
    else:
        return {"Status: model failed to run"}  

@app.get("/predict")
def Predict_model(text : str):
    prediction = model.predict(text)
    return {"Model": "{prediction}"}
    

        

class LocalSentimentAnalysis():
    pass


class comment():
    pass
"""

if __name__ == "__main__":
    start = HFSentimentAnalysis()
    start.predict("text")
    start.download




    """
    
    print("tet")
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
    labels = model.config.id2label
    print(labels) 
    print("Logits:", logits)
    print("Probabilities:", probs)
    print(float(probs[0][0]))
    """

