"""
Created by Andres Eufrasio Tinajero 
"""
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model import SentimentAnalysis
from uuid import UUID
from typing import Optional
from database_tools import DatabaseTools, DatabaseCon
from datetime import datetime
from lang_detection import DetectLanguage


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_methods=["*"],
    allow_headers=["*"],
)
"""Note pad
replace port with enviroment var
I need to put more contraints on comments doing things like .lower and removing emojis for normalization and for it to work better with the AI
also need to put that into the tests
"""

"""
Load model
"""
class Model_tools:
    def __init__(self):
        self.model = None
        self.name = None
        self.labels = None
        self.load_model()

    def load_model(self):
        conn = DatabaseCon.get_conn()

        try:
            db = DatabaseTools(conn)

            active_model = db.get_active_model()
            model_name = active_model or "unitary/toxic-bert"

            self.model = SentimentAnalysis(model_name=model_name)
            self.name, self.labels = self.get_info()

        except Exception as e:
            raise RuntimeError(
                f"Failure to load model: {e}"
            ) from e

        finally:
            DatabaseCon.put_conn(conn)

    def predict(self,text : str):
        return self.model.predict(text)
    
    #Return a tuple containing name and model labels[]
    def get_info(self):
        model_name = self.model.get_name()
        #convert to list from dict
        model_labels = list(self.model.get_labels().values())
        return model_name, model_labels
    
    def get_name(self):
        return self.model.get_name()
    
    def switch_model(self, model_name) -> bool:
        return self.model.switch_model(model_name)

    
    
system = Model_tools() 

"""Language detection"""
langDetect = DetectLanguage()


"""
pydantic shema
"""
class CommentIn(BaseModel):
    id: str
    content: str
    author_id: Optional[str] = None
    post_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None

class UserIn(BaseModel):
    id: str
    username: str
    created_at: Optional[datetime] = None
    banned: Optional[bool] = False

class PostIn(BaseModel):
    id: str
    content: str
    author_id: str
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

class ChangeModelIn(BaseModel):
    model_name: str




"""
Notes
Implement not just using toxic
"""

"""My background tasks"""
def process_comment(comment: CommentIn):
    conn = DatabaseCon.get_conn()

    try:
        db = DatabaseTools(conn)

        result = system.predict(comment.content)

        print(result)

        flagged = result.get("toxic", 0) > 0.4

        comment_id = db.create_comment(
            comment.content,
            comment.post_id,
            comment.author_id,
            comment.parent_comment_id
        )["id"]

        flag_id = db.create_flag(
            comment_id=comment_id,
            active=flagged
        )["id"]

        db.create_prediction(
            model_id=system.name,
            confidence=list(result.values()),
            flag_id=flag_id
        )

    except Exception as e:
        raise RuntimeError(
            f"Failure to process new comment: {e}"
        ) from e

    finally:
        DatabaseCon.put_conn(conn)
        

# API endpoints
@app.get("/")
def root():
    return {"Connection": "Healthy",
            "info" : "Please use /docs to see automatic documentation for API"
            }

@app.post("/create_user", status_code=201)
def create_user(user: UserIn):
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        dict_user_id = db.create_user(
        user.id,
        user.username,
        user.created_at,
        user.banned
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User was not created: {str(e)}")
    finally:
        DatabaseCon.put_conn(conn)
    return dict_user_id
        
@app.post("/create_post", status_code=201)
def create_post(post: PostIn):
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        dict_post_id = db.create_post(
        post.id,
        post.content,
        post.author_id,
        post.posted_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Post was not created: {str(e)}")
    finally:
        DatabaseCon.put_conn(conn)
    return dict_post_id


@app.post("/user_comments", status_code=202)
def post_comment(
    comment: CommentIn,
    background_tasks: BackgroundTasks
):
    if not comment.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty"
        )

    if len(comment.content) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be longer than 2000 characters"
        )
    process_comment(comment)
    return {"status": "added"}


@app.get("/flags", status_code=200)
def get_predictions():
    conn = DatabaseCon.get_conn()
    try:
        db = DatabaseTools(conn)
        flags = db.get_unreviewed_flags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flags were not retrieved: {str(e)}")
    finally:
        DatabaseCon.put_conn(conn)
    return flags

@app.post("/moderate", status_code=201)
def moderate_post(modDec: ModerationDecisionIn):
    conn = DatabaseCon.get_conn()

    try:
        db = DatabaseTools(conn)

        moderation = db.create_moderation_decision(
            modDec.comment_id,
            modDec.moderator_id,
            modDec.flag_id,
            modDec.decision,
            modDec.prediction_id
        )

        db.deactivate_flag(modDec.flag_id)

        return {
            "status": "success",
            "moderation": moderation,
            "comment_id": str(modDec.comment_id),
            "flag_id": str(modDec.flag_id),
            "decision": modDec.decision,
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Moderation failed: {str(e)}"
        )

    finally:
        DatabaseCon.put_conn(conn)


@app.get("/audit-log", status_code=200)
def get_audit_log():
    conn = DatabaseCon.get_conn()

    try:
        db = DatabaseTools(conn)
        audit_log = db.get_audit_log()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audit log was not retrieved: {str(e)}"
        )

    finally:
        DatabaseCon.put_conn(conn)

    return audit_log

@app.post("/model", status_code=201)
def change_model(model: ChangeModelIn):
    conn = DatabaseCon.get_conn()

    try:
        db = DatabaseTools(conn)

        old_model, _ = system.get_info()

        system_result = system.switch_model(model.model_name)

        if not system_result:
            return {
                "success": False,
                "error": "Model failed to load"
            }

        database_result = db.switch_model(model.model_name)

        if not database_result:
            system.switch_model(old_model)
            return {
                "success": False,
                "error": "Model loaded, but database update failed so model rolled back"
            }

        new_model, _ = system.get_info()

        if old_model != new_model:
            print("Model name change successful")

        return {
            "success": True,
            "model": system.get_name()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model could not be changed: {str(e)}"
        )

    finally:
        DatabaseCon.put_conn(conn)

@app.get("/model", status_code=200)
def get_active_model():
    conn = DatabaseCon.get_conn()

    try:
        db = DatabaseTools(conn)
        name = db.get_active_model()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Name could not be accessed {str(e)}"
        )

    finally:
        DatabaseCon.put_conn(conn)

    return name



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
