from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatSchema(BaseModel):
    message: str
    visitor_id: Optional[str] = None
    voice_enabled: Optional[bool] = False

class ChatActionSchema(BaseModel):
    type: str
    feature: Optional[str] = None
    media_id: Optional[str] = None

    class Config:
        extra = "allow"

class ChatResponseSchema(BaseModel):
    reply: str
    emotion: str
    intent: str
    risk_level: str
    recommended_feature: Optional[str] = "NONE"
    action: ChatActionSchema
    therapy: Dict[str, Any]
    audio_base64: Optional[str] = None