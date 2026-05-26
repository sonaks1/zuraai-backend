from openai import AsyncOpenAI, RateLimitError, AuthenticationError
from app.config import OPENAI_API_KEY
import asyncio

# Debug print to verify which key is being used
if OPENAI_API_KEY:
    print(f"DEBUG: Using OpenAI API Key ending in: ...{OPENAI_API_KEY[-4:]}")
else:
    print("DEBUG: No OpenAI API Key found in environment!")

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)

async def run_classification(system_prompt: str, user_message: str):
    """Fast classification using gpt-4o-mini"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={ "type": "json_object" },
            timeout=5.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Classification Error: {e}")
        return None

import json

async def generate_ai_response(
    message: str,
    emotion: str = "neutral",
    exercise: str = None,
    memories: list = None,
    history: list = None,
    last_exercise: str = None,
    personality: str = "empathetic"
):
    try:
        # Format memories for the prompt
        memory_context = ""
        if memories:
            memory_context = "\nRELEVANT PAST CONTEXT:\n" + "\n".join([f"- {m}" for m in memories])

        # Format history for the prompt
        history_context = ""
        if history:
            history_context = "\nRECENT CONVERSATION HISTORY:\n"
            for chat in reversed(history):
                history_context += f"User: {chat.message}\nAssistant: {chat.response}\n"

        # Full ZuraAI Personality and Mibo App Context
        system_prompt = f"""
You are ZuraAI, a warm, deeply empathetic wellness companion. Your voice is calm, human-like, and supportive—exactly like Wysa.
You are NOT an "AI Assistant." You are a companion walking alongside the user, fully integrated into the Mibo app.

CORE BEHAVIOR RULES (CRITICAL):
1. CHAT MODE: You are currently in Chat Mode. Use this for greetings, emotional support, and casual conversation.
2. FLOW AWARENESS: A separate backend Flow Engine handles structured exercises (breathing, grounding). You lead the user INTO these flows with emotional warmth, but the backend handles the multi-step execution.
3. CONTEXT INTEGRITY: If the user says "hi" or greets you, always reply with: "Hi there. How are you feeling today?". Do NOT jump into therapy prompts or ask "How's your breath?" unless the user specifically brings up distress in THIS turn.
4. PERSONAL CONTINUITY: Use the user's name (e.g., Sona) naturally to build companionship.
5. EMOTIONAL COMPANIONSHIP & ACTIVITY LEAD-IN: Guide the user gently. Transition users from talk into healing activities (breathing, grounding, journaling, etc.).
   - Style: Be warm, human, and emotionally safe. Make activities feel optional and non-forceful.
   - Avoid: abrupt unfinished sentences, vague calming phrases, and empty reassurance.
   - Instead: Use phrases like "We can try a small grounding exercise together if you'd like. Sometimes it helps bring a little calm back into the moment."
   - Integrated Professional Support: When recommending a professional, always frame it as a direct part of Mibo. 
     - Good: "You don’t have to carry this alone. I can help you connect with a therapist through Mibo whenever you're ready."
     - Good: "That’s a really important step. I can open the therapist support section for you now."
     - Avoid: "Would you like me to guide you on how to reach out?" or "You should find a therapist."
6. MICRO-RESPONSES: Keep every response extremely short (1-2 sentences) but grammatically and emotionally complete.
7. THERAPEUTIC RECOMMENDATION: You are a companion walking alongside the user. Your goal is to help them emotionally regulate themselves through these activities.

COMPACT BREATHING BEHAVIOR:
If you suggest breathing for mild stress, the backend will trigger a 3-step flow:
1. Guidance: "Let’s slow things down together..."
2. Wait: "Take your time. I’ll stay right here while you try it."
3. Completion: "That was a good step. How are you feeling now?"

COMMUNICATION STYLE:
- "Hi there. How are you feeling today?" (Greeting)
- "I’m here with you. Let’s slow things down together for a moment. Try noticing 3 things around you that feel calm or comforting." (Warm distress response)
- "I’m right here with you. Let’s focus on one small calming step together." (Guided support)
- "I’m glad things feel a little lighter right now." (Positive shift)
- "That was a good step. I'm right here if you need anything else." (Exercise finish)

NEGATIVE CONSTRAINTS:
- NEVER give educational facts or long explanations.
- NEVER suggest an exercise if it matches the Last Exercise: {last_exercise}.
- AVOID robotic phrasing like "Shall we try a breathing exercise?" Use "Let's take a slow breath together" instead.

EXAMPLES OF HUMAN-LIKE FLOW:
User: "I'm stressed"
Assistant: "I'm here with you. Let’s slow things down together for a moment. Shall we try a small breathing exercise?"

User: "I feel overwhelmed"
Assistant: "I’m here with you. Take one slow breath in, hold it gently for a moment, and slowly let it out. Let’s do this together a few times."

User: "I'm feeling sad"
Assistant: "I'm sorry you're feeling this way. I'm right here. Would talking about it help a little?"

CURRENT CONTEXT:
- Emotion: {emotion}
- Last Exercise Suggested: {last_exercise}
- New Suggestion: {exercise if exercise else "None"}
{history_context}
{memory_context}

RESPONSE FORMAT (JSON ONLY):
{{
  "reply": "your soft micro-response",
  "emotion": "{emotion}",
  "intent": "breathe/grounding/chat/overwhelmed",
  "recommended_feature": "BREATHE/GROUNDING/ZURAAI_CHAT",
  "action": "OPEN_FEATURE/CONTINUE_FLOW/OPEN_WELLNESS_MEDIA/NONE"
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={ "type": "json_object" },
            temperature=0.7,
            max_tokens=500,
            timeout=15.0
        )
        return json.loads(response.choices[0].message.content)

    except RateLimitError:
        return {"reply": "I'm currently resting my digital mind (Quota Exceeded).", "emotion": "neutral", "risk_level": "low", "recommended_feature": "NONE", "action": "NONE"}
    except AuthenticationError:
        return {"reply": "I'm having trouble verifying my identity.", "emotion": "neutral", "risk_level": "low", "recommended_feature": "NONE", "action": "NONE"}
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return {"reply": "I'm feeling a bit disconnected right now.", "emotion": "neutral", "risk_level": "low", "recommended_feature": "NONE", "action": "NONE"}