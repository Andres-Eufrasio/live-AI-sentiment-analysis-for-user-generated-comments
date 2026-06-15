from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

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

class Prediction(BaseModel):
    result: float
    label: str

class Comment(BaseModel):
    Username: str
    Comment: str
    Time: str
    

#temp datastructure that will act as database until it is created
database = []
queue = []


@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/predictions")
def recive_prediction(prediction: Prediction):
    #need to check prediction socre and then hold it depending 
    database.append(prediction)

@app.get("/predictions")
def get_prediction():
    return {"Prediction": f"{database}"}

@app.post("/user_comments")
def get_comment(comment: Comment):
    queue.append(Comment)

@app.get("/user_comments")
def get_comment():
    temp = queue.pop()
    PredComments
    return {"Comment" : f"queue.pop"}

@app.get("/all_comments")
def get_all_comments:
    return {}





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)