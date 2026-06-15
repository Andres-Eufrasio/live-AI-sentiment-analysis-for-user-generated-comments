"""
Created by Andres Eufrasio Tinajero 
"""
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from model import SentimentAnalysis
from uuid import UUID
from typing import Optional
from database_tools import DatabaseTools, DatabaseCon


app = FastAPI()

"""Note pad
Since things are a little messed up between my database and api I need to reslove them.
To begin let's just go through one process and fix it.
User commnet in
precition
to save prediction
"""

"""
Load model
"""
class Main():
    def __init__(self):
        self.load_model()

    def load_model(self):
        self.model=SentimentAnalysis()
        print("Model loaded")

    def predict(self,text : str):
        return self.model.predict(text)
system = Main() 

"""
Load database connection
"""
with DatabaseCon() as conn:
    database = DatabaseTools(conn)

"""
pydantic shema
"""
class CommentIn(BaseModel):
    content: str
    author_id: UUID 
    post_id: UUID
    parent_comment_id: Optional[UUID] = None
    context: Optional[str] = None

class UserReportIn(BaseModel):
    user_id: UUID 
    comment_id: UUID
    reason: str
    category: str

class FlagIn(BaseModel):
    comment_id: UUID
    user_report_id: Optional[UUID] = None
    prediction_score: Optional[float] = None  

class PredictionIn(BaseModel):
    flag_id: UUID
    model_id: UUID
    confidence: float 
    label: str

class ModerationDecisionIn(BaseModel):
    comment_id: UUID
    moderator_id: UUID
    flag_id: UUID
    prediction_id: Optional[UUID] = None
    decision: bool      
    
#temp datastructure that will act as database until it is created
queue = []


"""My background tasks"""
def process_comment(comment: CommentIn):
    result = system.predict(comment.content)
    database.create_comment(
    comment.content,
    comment.post_id,
    comment.author_id,
    comment.parent_comment_id,
    comment.context,
    )
    # add prediction


# API endpoints
@app.get("/")
def root():
    return {"Connection": "Established"}

@app.post("/user_comments", status_code=201)
def post_comment(comment: CommentIn, background_tasks: BackgroundTasks):
    if comment.content == "":
        # bad request
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    if len(comment.content) > 2000:
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
def receive_prediction(prediction: PredictionIn):
    database.append(prediction)
    return {"status": "saved"}

# finish this bit
@app.get("/predictions")
def get_predictions():
    return {"predictions": database}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
