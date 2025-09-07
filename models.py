from pydantic import BaseModel
from datetime import datetime

class Note(BaseModel):
    uid: str
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime 
