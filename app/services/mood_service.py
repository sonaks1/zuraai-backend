from sqlalchemy.orm import Session
from app.models.mood_model import MoodHistory, UserTrigger, WellnessProgress
from app.models.user_model import User
from datetime import datetime, timedelta
from app.services.openai_service import run_classification
import json

def track_mood(db: Session, user_id: int, emotion: str, severity: float, context: str = None):
    """Saves the detected emotion to the user's mood history with context"""
    mood_entry = MoodHistory(
        user_id=user_id,
        emotion=emotion,
        mood=str(severity),
        severity=severity,
        context=context,
        timestamp=datetime.utcnow()
    )
    db.add(mood_entry)
    db.commit()

async def extract_and_update_user_name(db: Session, user_id: int, message: str):
    """Uses AI to extract the user's name if they shared it and updates the User record"""
    system_prompt = """
    Analyze the message to see if the user is introducing themselves or sharing their name.
    If they share their name, return it as a JSON object: {"name": "DetectedName"}.
    If no name is shared, return {}.
    Example: "i am sona" -> {"name": "Sona"}
    """
    
    response = await run_classification(system_prompt, message)
    try:
        data = json.loads(response) if response else {}
        name = data.get("name")
        if name:
            update_user_name(db, user_id, name)
    except Exception as e:
        print(f"Name Extraction Error: {e}")

def update_user_name(db: Session, user_id: int, name: str):
    """Updates the user's name in the database"""
    if not name:
        return
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        db.commit()

async def analyze_and_track_triggers(db: Session, user_id: int, message: str):
    """Uses AI to extract potential stressors/triggers from the message"""
    system_prompt = """
    Identify any specific stressors or emotional triggers in the user's message.
    Examples: "work stress", "family conflict", "health anxiety", "financial worry".
    Return a JSON list of strings. If none, return [].
    """
    
    response = await run_classification(system_prompt, message)
    try:
        triggers = json.loads(response) if response else []
        track_triggers(db, user_id, triggers)
    except Exception as e:
        print(f"Trigger Tracking Error: {e}")

def track_triggers(db: Session, user_id: int, triggers: list):
    """Saves the extracted triggers to the database"""
    if not triggers:
        return
    for t_name in triggers:
        trigger = db.query(UserTrigger).filter(
            UserTrigger.user_id == user_id,
            UserTrigger.trigger_name == t_name.lower()
        ).first()
        
        if trigger:
            trigger.frequency += 1
            trigger.last_detected = datetime.utcnow()
        else:
            new_trigger = UserTrigger(user_id=user_id, trigger_name=t_name.lower())
            db.add(new_trigger)
    db.commit()

def get_mood_insights(db: Session, user_id: int):
    """Calculates mood trends and retrieves top triggers"""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Mood Trend
    recent_moods = db.query(MoodHistory).filter(
        MoodHistory.user_id == user_id,
        MoodHistory.timestamp >= seven_days_ago
    ).order_by(MoodHistory.timestamp.desc()).all()
    
    trend = "stable"
    if len(recent_moods) > 3:
        first_half = sum(m.severity for m in recent_moods[len(recent_moods)//2:])
        second_half = sum(m.severity for m in recent_moods[:len(recent_moods)//2])
        if second_half < first_half: trend = "improving"
        elif second_half > first_half: trend = "declining"

    # Top Triggers
    top_triggers = db.query(UserTrigger).filter(
        UserTrigger.user_id == user_id
    ).order_by(UserTrigger.frequency.desc()).limit(3).all()
    
    return {
        "trend": trend,
        "top_triggers": [t.trigger_name for t in top_triggers],
        "recent_emotions": [m.emotion for m in recent_moods[:5]]
    }

def track_wellness_progress(db: Session, user_id: int, exercise_id: str, exercise_name: str, feedback: str = None):
    """Records a completed wellness exercise"""
    progress = WellnessProgress(
        user_id=user_id,
        exercise_id=exercise_id,
        exercise_name=exercise_name,
        feedback=feedback,
        completed_at=datetime.utcnow()
    )
    db.add(progress)
    db.commit()

def get_wellness_summary(db: Session, user_id: int):
    """Gets total exercises completed this week"""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    count = db.query(WellnessProgress).filter(
        WellnessProgress.user_id == user_id,
        WellnessProgress.completed_at >= seven_days_ago
    ).count()
    return count

def get_exercise_effectiveness(db: Session, user_id: int):
    """Retrieves which exercises were helpful vs unhelpful based on feedback"""
    records = db.query(WellnessProgress).filter(
        WellnessProgress.user_id == user_id
    ).order_by(WellnessProgress.completed_at.desc()).limit(10).all()
    
    helpful = []
    unhelpful = []
    
    for r in records:
        if not r.feedback: continue
        fb = r.feedback.lower()
        # Simple keyword matching for effectiveness
        is_helpful = any(word in fb for word in ["better", "helped", "changed", "good", "calm", "lighter", "relief"])
        is_unhelpful = any(word in fb for word in ["no change", "not work", "same", "worse", "didn't help"])
        
        if is_helpful:
            helpful.append(r.exercise_id)
        elif is_unhelpful:
            unhelpful.append(r.exercise_id)
            
    return {"helpful": list(set(helpful)), "unhelpful": list(set(unhelpful))}

def get_recent_emotions(db: Session, user_id: int, limit: int = 5):
    """Retrieves recent emotions for personalization"""
    entries = db.query(MoodHistory).filter(
        MoodHistory.user_id == user_id
    ).order_by(MoodHistory.id.desc()).limit(limit).all()
    return [entry.emotion for entry in entries]
