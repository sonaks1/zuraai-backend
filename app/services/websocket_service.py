from fastapi import WebSocket
import json
from app.services.emotion_service import detect_emotion
from app.services.crisis_service import detect_crisis
from app.services.intent_service import detect_intent
from app.services.therapy_service import get_therapeutic_recommendation
from app.services.action_router import route_action
from app.services.openai_service import generate_ai_response
from app.services.memory_service import save_memory

import asyncio

from app.services.redis_service import redis_client
from app.services.therapy_service import get_next_flow_step, get_therapeutic_recommendation
from app.services.flow_service import get_session_state, save_session_state, handle_flow_logic
import json

from app.database import SessionLocal
from app.services.chat_history_service import get_chat_history, save_chat_history

async def websocket_chat(websocket: WebSocket, user_id: int):
    await websocket.accept()
    db = SessionLocal()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()

            # 0. Load Session State
            session_state = get_session_state(user_id)

            # 1. Parallel Analysis Engines
            emotion_task = detect_emotion(user_message)
            crisis_task = detect_crisis(user_message)
            intent_task = detect_intent(user_message)
            
            emotion_data, crisis_data, intent_data = await asyncio.gather(
                emotion_task, crisis_task, intent_task
            )

            # 2. Flow Orchestration (Priority 1)
            flow_reply, session_state, flow_active = handle_flow_logic(user_message, session_state, intent_data)
            
            if flow_active:
                save_session_state(user_id, session_state)
                save_chat_history(db, user_id, user_message, flow_reply, session_state.get("last_emotion", "neutral"))
                
                active_flow = session_state.get("active_flow")
                await websocket.send_json({
                    "reply": flow_reply,
                    "emotion": session_state.get("last_emotion", "neutral"),
                    "intent": "continuation",
                    "risk_level": "low",
                    "recommended_feature": active_flow.upper() if active_flow else "BREATHE",
                    "action": {
                        "type": "CONTINUE_FLOW", 
                        "feature": active_flow.upper() if active_flow else "BREATHE",
                        "flow": active_flow, 
                        "step": session_state["current_step"]
                    },
                    "therapy": {"exercise": flow_reply, "type": "Flow"}
                })
                continue

            # 3. Contextual Data
            from app.services.memory_search_service import search_memory
            memory_results = search_memory(user_message)
            retrieved_memories = memory_results.get("documents", [[]])[0] if memory_results else []
            history = get_chat_history(db, user_id, limit=5)

            # 4. Safety Check & State Transitions
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
                redis_client.delete(f"zura_session:{user_id}")
            elif is_severe:
                final_reply = "I can hear how much you're carrying right now. It might be helpful to talk this through with someone who can offer specialized support. Would you like to see how to connect with a professional?"
                recommended_feature = "THERAPIST_BOOKING"
                action_data = {"type": "THERAPIST_ESCALATION", "feature": "THERAPIST_BOOKING"}
                session_state.update({"last_severity": current_severity, "last_emotion": current_emotion})
            else:
                # Rule: Panic detected -> crisis calming flow (Slow Breathing)
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
                    # 5. Generate AI Response (Normal Chat)
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
                
                # Check if the AI or rules recommended a specific flow
                intent_ai = ai_output.get("intent", "").lower()
                reply_ai = final_reply.lower()
                
                if "breathe" in intent_ai or "breathing" in intent_ai or "breath" in reply_ai:
                    # Slow breathing for panic or high anxiety
                    flow_name = "breathing" if current_emotion == "panic" else "compact_breathing"
                    
                    session_state.update({
                        "active_flow": None,
                        "pending_flow": flow_name,
                        "awaiting_confirmation": True,
                        "current_step": 0 if current_emotion != "panic" else 1, # Start at 1 if we already gave the first step
                        "last_emotion": current_emotion,
                        "last_severity": current_severity
                    })
                    # If it was an immediate transition (panic/sadness rules), set it to active immediately?
                    # The instructions say "wait for backend to take over", so we keep it pending.
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
                        "last_emotion": emotion_data["emotion"]
                    })
                
                save_session_state(user_id, session_state)

                action_routing = route_action(
                    ai_output.get("intent", intent_data["intent"]), 
                    ai_output.get("emotion", emotion_data["emotion"]), 
                    ai_output.get("risk_level", crisis_data["risk_level"])
                )
                action_data = action_routing["action"]
                recommended_feature = action_routing["recommended_feature"]

            # 6. Post-Response Tasks
            save_chat_history(db, user_id, user_message, final_reply, emotion_data["emotion"])
            asyncio.create_task(asyncio.to_thread(save_memory, user_id, user_message, emotion_data["emotion"], intent_data["intent"]))

            # 7. Send structured response back
            await websocket.send_json({
                "reply": final_reply,
                "emotion": emotion_data["emotion"],
                "intent": intent_data["intent"],
                "risk_level": crisis_data["risk_level"],
                "recommended_feature": recommended_feature,
                "action": action_data,
                "therapy": get_therapeutic_recommendation(emotion_data["emotion"])
            })


    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        db.close()
        await websocket.close()