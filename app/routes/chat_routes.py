from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.chat_schema import ChatSchema

from app.database import SessionLocal

from app.utils.get_current_user import (
    get_current_user
)

from app.services.emotion_service import (
    detect_emotion
)

from app.services.crisis_service import (
    detect_crisis
)

from app.services.therapy_service import (
    get_therapeutic_recommendation
)

from app.services.action_router import (
    route_action
)

from app.services.personalization_service import (
    personality_mode
)

from app.services.memory_service import (
    save_memory
)

from app.services.memory_search_service import (
    search_memory
)

from app.services.chat_history_service import (
    get_chat_history,
    save_chat_history
)

from app.services.openai_service import (
    generate_ai_response
)

router = APIRouter(
    prefix="/chat"
)

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

from app.services.intent_service import (
    detect_intent
)

from app.services.flow_service import (
    get_session_state,
    save_session_state,
    handle_flow_logic
)

from app.schemas.chat_schema import ChatSchema, ChatResponseSchema

import asyncio

@router.post("/", response_model=ChatResponseSchema)
async def chat(
    data: ChatSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 0. Load Session State
    session_state = get_session_state(current_user.id)
    user_message = data.message.strip()

    # 1. Parallel Analysis (Matches WebSocket logic for consistency)
    emotion_task = detect_emotion(user_message)
    crisis_task = detect_crisis(user_message)
    intent_task = detect_intent(user_message)
    
    emotion_data, crisis_data, intent_data = await asyncio.gather(
        emotion_task, crisis_task, intent_task
    )

    # 2. Flow Orchestration (Priority 1)
    flow_reply, session_state, flow_active = handle_flow_logic(user_message, session_state, intent_data)
    
    if flow_active:
        save_session_state(current_user.id, session_state)
        await asyncio.to_thread(save_chat_history, db, current_user.id, user_message, flow_reply, session_state.get("last_emotion", "neutral"))
        
        active_flow = session_state.get("active_flow")
        return {
            "reply": flow_reply,
            "emotion": session_state.get("last_emotion", "neutral"),
            "intent": "continuation",
            "risk_level": "low",
            "recommended_feature": active_flow.upper() if active_flow else "BREATHE",
            "action": {
                "type": "CONTINUE_FLOW", 
                "feature": active_flow.upper() if active_flow else "BREATHE",
                "flow": active_flow, 
                "step": session_state.get("current_step")
            },
            "therapy": {"exercise": flow_reply, "type": "Flow"}
        }

    # 3. Safety Check & State Transitions
    last_severity = session_state.get("last_severity", 0.0)
    current_severity = emotion_data["severity"]
    last_emotion = session_state.get("last_emotion", "neutral")
    current_emotion = emotion_data["emotion"]

    # Rule: Distress becomes severe -> therapist escalation
    is_severe = current_severity > 0.8 or crisis_data["risk_level"] == "moderate"
    
    if crisis_data["risk_level"] == "critical":
        final_reply = "I'm really sorry you're going through this much pain right now. You don't have to face this alone. I strongly encourage connecting with immediate emotional support or a licensed professional through Mibo’s support system."
        recommended_feature = "INSTANT_SUPPORT"
        action_data = {"type": "EMERGENCY_SUPPORT", "feature": "INSTANT_SUPPORT"}
        redis_client.delete(f"zura_session:{current_user.id}")
        await asyncio.to_thread(save_chat_history, db, current_user.id, user_message, final_reply, current_emotion)
        return {
            "reply": final_reply,
            "emotion": current_emotion,
            "intent": "crisis",
            "risk_level": "critical",
            "recommended_feature": recommended_feature,
            "action": action_data,
            "therapy": get_therapeutic_recommendation(current_emotion)
        }
    elif is_severe:
        final_reply = "I can hear how much you're carrying right now. It might be helpful to talk this through with someone who can offer specialized support. Would you like to see how to connect with a professional?"
        recommended_feature = "THERAPIST_BOOKING"
        action_data = {"type": "THERAPIST_ESCALATION", "feature": "THERAPIST_BOOKING"}
        session_state.update({"last_severity": current_severity, "last_emotion": current_emotion})
        ai_output = {"intent": "Therapist Booking"} # For history
    else:
        # Rule: Panic detected -> crisis calming flow
        if current_emotion == "panic":
            ai_output = {
                "reply": "I'm right here with you. Let’s slow things down together. Take a slow breath in...",
                "intent": "breathe",
                "recommended_feature": "BREATHE"
            }
        # Rule: Sadness increases -> grounding support
        elif current_emotion == "sadness" and current_severity > last_severity and last_emotion == "sadness":
            ai_output = {
                "reply": "I can feel things getting a bit heavier. Let's try to ground ourselves in the present moment together. Can you name 3 things you see right now?",
                "intent": "grounding",
                "recommended_feature": "GROUNDING"
            }
        else:
            # 4. Generate AI Response
            # Context for AI
            from app.services.memory_search_service import search_memory
            memory_results = search_memory(user_message)
            retrieved_memories = memory_results.get("documents", [[]])[0] if memory_results else []
            history = get_chat_history(db, current_user.id, limit=5)

            ai_output = await generate_ai_response(
                message=user_message,
                emotion=current_emotion,
                memories=retrieved_memories,
                history=history,
                last_exercise=session_state.get("last_exercise"),
                personality="empathetic"
            )
        
        final_reply = ai_output.get("reply", "I'm here for you.")
        recommended_feature = ai_output.get("recommended_feature", "ZURAAI_CHAT")
        
        # 5. Post-AI State Updates (Check if AI or rules suggested a flow)
        intent_ai = ai_output.get("intent", "").lower()
        reply_ai = final_reply.lower()
        
        if "breathe" in intent_ai or "breathing" in intent_ai or "breath" in reply_ai:
            flow_name = "breathing" if current_emotion == "panic" else "compact_breathing"
            session_state.update({
                "active_flow": None,
                "pending_flow": flow_name,
                "awaiting_confirmation": True,
                "current_step": 0 if current_emotion != "panic" else 1,
                "last_emotion": current_emotion,
                "last_severity": current_severity
            })
        elif "grounding" in intent_ai or "5-4-3-2-1" in user_message.lower() or "grounding" in reply_ai:
            session_state.update({
                "active_flow": None,
                "pending_flow": "grounding",
                "awaiting_confirmation": True,
                "current_step": 1 if "grounding" in ai_output.get("intent", "") and "sadness" in current_emotion else 0,
                "last_emotion": current_emotion,
                "last_severity": current_severity
            })
        elif any(phrase in reply_ai for phrase in ["talking", "weighing on your mind", "help a little", "here to listen", "share whatever", "little as you'd like"]):
            session_state.update({
                "active_flow": None,
                "pending_flow": "sadness_support",
                "awaiting_confirmation": True,
                "current_step": 0,
                "last_emotion": current_emotion,
                "last_severity": current_severity
            })
        
        save_session_state(current_user.id, session_state)

        # 6. Final Routing & History
        action_routing = route_action(
            ai_output.get("intent", intent_data["intent"]), 
            current_emotion, 
            crisis_data["risk_level"]
        )
        action_data = action_routing["action"]
        recommended_feature = action_routing["recommended_feature"]

    # Set media session flag if applicable
    if action_data["type"] == "OPEN_WELLNESS_MEDIA":
        session_state["media_session_active"] = True
        save_session_state(current_user.id, session_state)
    
    await asyncio.to_thread(save_chat_history, db, current_user.id, user_message, final_reply, current_emotion)
    asyncio.create_task(asyncio.to_thread(save_memory, current_user.id, user_message, current_emotion, intent_data["intent"]))

    return {
        "reply": final_reply,
        "emotion": current_emotion,
        "intent": ai_output.get("intent", intent_data["intent"]),
        "risk_level": crisis_data["risk_level"],
        "recommended_feature": recommended_feature,
        "action": action_data,
        "therapy": get_therapeutic_recommendation(current_emotion)
    }