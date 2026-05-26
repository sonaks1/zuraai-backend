from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatSchema(BaseModel):
    message: str

class ChatActionSchema(BaseModel):
    type: str
    feature: str
    media_id: Optional[str] = None

    class Config:
        extra = "allow"

class ChatResponseSchema(BaseModel):
    reply: str
    emotion: str
    intent: str
    risk_level: str
    recommended_feature: str
    action: ChatActionSchema
    therapy: Dict[str, Any]