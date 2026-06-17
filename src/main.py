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
from datetime import datetime

print("start")
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
        try:
            self.model=SentimentAnalysis()
            name, labels = self.get_info()
            #flush info to ensure it gets printed
            print("Model loaded")
            print(f"Model name: {name} \n Labels: {labels}", flush=True)
        except Exception as e:
            raise RuntimeError(f"Model failed to load: {e}")

    def predict(self,text : str):
        return self.model.predict(text)
    
    #Return a tuple containing name and model labels[]
    def get_info(self):
        model_name = self.model.get_name()
        #convert to list from dict
        model_labels = list(self.model.get_labels().values())
        return model_name, model_labels
system = Main() 



with DatabaseCon() as conn:
    database = DatabaseTools(conn)

"""
pydantic shema
"""
class CommentIn(BaseModel):
    content: str
    author_id: Optional[UUID] = None
    post_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None

class UserIn(BaseModel):
    id: str
    username: str
    created_at: Optional[datetime] = None
    banned: Optional[bool] = False

class PostIn(BaseModel):
    content: str
    user_id: str
    id: Optional[UUID] = None
    posted_time: Optional[datetime] = None

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
    model_name: str
    confidence: float 
    label: str

class ModerationDecisionIn(BaseModel):
    comment_id: UUID
    moderator_id: UUID
    flag_id: UUID
    prediction_id: Optional[UUID] = None
    decision: bool      
    

queue = []


"""My background tasks"""
def process_comment(comment: CommentIn):
    result = system.predict(comment.content)
    print(result)
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        db.create_comment(
        comment.content,
        comment.post_id,
        comment.author_id,
        comment.parent_comment_id,
        )
    finally:
        DatabaseCon.put_conn(conn)


# API endpoints
@app.get("/")
def root():
    return {"Connection": "Established"}

@app.post("/create_user", status_code=201)
def create_user(user: UserIn):
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        user_id = db.create_user(
        user.id,
        user.username,
        user.created_at,
        user.banned
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User was not created: {str(e)}")
    finally:
        DatabaseCon.put_conn(conn)
    return {"id": f"{user_id}"}
        
@app.post("/create_post", status_code=201)
def create_post(post: PostIn):
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        post_id = db.create_user(
        post.id,
        post.content,
        post.author_id,
        post.posted_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Post was not created: {str(e)}")
    finally:
        DatabaseCon.put_conn(conn)
    return {"post_id": f"{post_id}"}


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


# finish this bit
@app.get("/predictions")
def get_predictions():
    return {"predictions": database}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
