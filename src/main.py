from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from model import SentimentAnalysis

"""
Created by Andres Eufrasio Tinajero 
May 1st 2026

Todo:
input output for the model
input output from the database
input output from the website
validation
input output for online model
"""

    
app = FastAPI()
class Main():
    def __init__(self):
        self.load_model()

    def load_model(self):
        self.model=SentimentAnalysis()
        print("Model loaded")

    def predict(self,text : str):
        return self.model.predict(text)
system = Main() 

class Prediction(BaseModel):
    result: float
    label: str

class Comment(BaseModel):
    comment: str
    
#temp datastructure that will act as database until it is created
database = []
queue = []


# Fast API Background task
def process_comment(comment: Comment):
    result = system.predict(comment.comment)
    print(result)  # Replace with DB write

# API endpoints
@app.get("/")
def root():
    return {"Connection": "Established"}

@app.post("/user_comments", status_code=201)
def post_comment(comment: Comment, background_tasks: BackgroundTasks):
    if comment.comment == "":
        # bad request
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    if len(comment.comment) > 2000:
        # bad request
        raise HTTPException(status_code=400, detail="Comment cannot be longer than 2000 characters")
    background_tasks.add_task(process_comment, comment)
    return {"status": "queued"}

@app.get("/user_comments",status_code=200)
def get_next_comment():
    if not queue:
        raise HTTPException(status_code=404, detail="Queue is empty")
    return {"status": "queue is not empty"}



@app.post("/predictions", status_code=201)
def receive_prediction(prediction: Prediction):
    database.append(prediction)
    return {"status": "saved"}

# finish this bit
@app.get("/predictions")
def get_predictions():
    return {"predictions": database}






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
