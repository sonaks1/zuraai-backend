from sqlalchemy.orm import Session

from app.models.chat_model import ChatHistory

def save_chat_history(
    db: Session,
    user_id: int,
    message: str,
    response: str,
    emotion: str
):
    chat = ChatHistory(
        user_id=user_id,
        message=message,
        response=response,
        emotion=emotion
    )
    db.add(chat)
    db.commit()

def get_chat_history(db: Session, user_id: int, limit: int = 5):
    """Retrieve the most recent chat history for a user"""
    return db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.id.desc()).limit(limit).all()