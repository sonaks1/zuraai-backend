
import json
from app.services.redis_service import redis_client, SimpleCache
from app.services.therapy_service import get_next_flow_step

def get_session_state(user_id: int):
    session_key = f"zura_session:{user_id}"
    try:
        state_data = redis_client.get(session_key)
        if state_data:
            return state_data if isinstance(state_data, dict) else json.loads(state_data)
    except Exception as e:
        print(f"Redis Error (get): {e}")
    return {}

def save_session_state(user_id: int, state: dict):
    session_key = f"zura_session:{user_id}"
    try:
        if isinstance(redis_client, SimpleCache):
            redis_client.set(session_key, state)
        else:
            redis_client.set(session_key, json.dumps(state), ex=3600)
    except Exception as e:
        print(f"Redis Error (save): {e}")

def handle_flow_logic(user_message: str, session_state: dict, intent_data: dict):
    """
    Returns (reply, updated_state, flow_active)
    If flow_active is True, the reply should be sent and further AI processing skipped.
    """
    user_msg_lower = user_message.lower().strip()
    
    # 1. Detect Greetings & Reset Confirmation if needed
    is_greeting = intent_data.get("intent") == "General chat" and any(word in user_msg_lower for word in ["hi", "hello", "hey", "hii", "howdy", "sup"])
    
    if is_greeting:
        session_state["awaiting_confirmation"] = False
        session_state["pending_flow"] = None
        session_state["active_flow"] = None
        return None, session_state, False

    # 2. Continuation Check
    continuations = ["ok", "okay", "yes", "yeah", "sure", "done", "next", "continue", "go on", "yes please", "we can try", "i would like that", "let's do it", "let's try", "yep", "yup", "give"]
    is_continuation = user_msg_lower in continuations

    # 3. Media Session Follow-up
    # ONLY trigger if the user explicitly says "media_finished" 
    # OR if they say "yes/done" immediately after a media action was triggered.
    if user_msg_lower == "media_finished":
        session_state["media_session_active"] = False
        return "Welcome back. How are you feeling now?", session_state, True

    # If the user is in an active flow, continuations progress it.
    # If they are NOT in a flow, continuations might be for a "Pending Flow" (Confirmation).
    active_flow = session_state.get("active_flow")
    current_step = session_state.get("current_step", 0)

    # Step A: Transition from "Awaiting Confirmation" -> "Active Flow"
    if not active_flow and is_continuation and session_state.get("awaiting_confirmation"):
        active_flow = session_state.get("pending_flow")
        current_step = 0
        session_state["awaiting_confirmation"] = False
        session_state["pending_flow"] = None
        session_state["active_flow"] = active_flow
        session_state["current_step"] = 0
        # Clear media flag if we start a new flow
        session_state["media_session_active"] = False

    # Step B: Flow Execution
    if active_flow:
        # If the user is in an active flow but says something that is NOT a continuation,
        # we "fail" the flow and move to emotional conversation mode (AI Chat).
        if not is_continuation:
            session_state["active_flow"] = None
            session_state["current_step"] = 0
            return None, session_state, False

        next_text = get_next_flow_step(active_flow, current_step)
        if next_text:
            session_state["current_step"] = current_step + 1
            session_state["last_exercise"] = active_flow
            return next_text, session_state, True
        else:
            # Flow finished
            session_state["active_flow"] = None
            session_state["current_step"] = 0
            session_state["media_session_active"] = False # Ensure media flag is cleared
            return None, session_state, False

    return None, session_state, False
