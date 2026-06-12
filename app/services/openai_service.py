from openai import AsyncOpenAI, RateLimitError, AuthenticationError
from app.config import OPENAI_API_KEY
import asyncio
import json

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
            timeout=10.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Classification Error: {e}")
        return None

async def generate_unified_zura_response(
    message: str,
    previous_emotion: str = None,
    memories: list = None,
    history: list = None,
    last_exercise: str = None,
    completed_exercises: list = None,
    refused_exercises: list = None,
    personalized_context: str = "",
    audio_metadata: dict = None
):
    try:
        memory_context = "\nPAST: " + "; ".join(memories) if memories else ""
        history_context = ""
        if history:
            history_context = "\nLAST 3:\n" + "\n".join([f"U: {c.message}\nA: {c.response}" for c in reversed(history[:3])])
        
        system_prompt = f"""
You are ZuraAI, a warm and professional wellness companion. Your goal is to provide directive coaching with deep empathy and expert-level synthesis.
RECOGNITION & SYNTHESIS RULES:
1. Synthesize Context: If the user provides new info (e.g., "periods" after "pain"), acknowledge the connection immediately.
2. Practical Care First: For sadness, crying, or physical discomfort, prioritize practical self-care (rest, hydration, warmth) and emotional check-ins before suggesting structured exercises.
3. Exercise Relevance: 
   - FOR ANXIETY/PANIC: Use 'grounding' or 'breathing'.
   - FOR SADNESS/OVERWHELM: Use 'reflection_flow', 'self_esteem', or 'thought_reframing'. AVOID 'grounding' unless they feel disconnected.
4. Directive Initiative: Take initiative with 1-2 small relaxation steps. Evolve these steps each turn; do not repeat.
5. Smooth Transitions: Before suggesting a flow, validate the user's current state. If they just "ok'd" a small step, acknowledge it ("Thank you for trying that...") before moving to a structured flow.
6. Professional Depth: For sadness/crying, ask about the specific quality of the feeling (e.g., "Does it feel like exhaustion, loneliness, or just a heavy mix of everything?") to show deep listening.

{personalized_context}
{memory_context}
{history_context}

Return ONLY JSON:
{{
  "analysis": {{"emotion": "...", "severity_score": 0.0, "risk_level": "low/moderate/critical", "intent": "...", "triggers": [], "name": "..."}},
  "reply": "...",
  "suggested_flow": "flow_id_or_null",
  "recommended_feature": "...",
  "action": {{"type": "NONE/OPEN_FEATURE/CONTINUE_FLOW", "feature": "..."}}
}}
FLOWS: breathing, compact_breathing, box_breathing, 478_breathing, grounding, tension_release, thought_reframing, body_scan, self_esteem, reflection_flow, assessment, onboarding.
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={ "type": "json_object" },
            temperature=0.7,
            timeout=10.0
        )
        return json.loads(response.choices[0].message.content)
    except RateLimitError:
        return {"analysis": {"emotion": "neutral", "severity_score": 0.2, "risk_level": "low", "intent": "chat"}, "reply": "I'm here for you, but I'm a bit overwhelmed right now. Let's take a slow breath together.", "suggested_flow": "breathing", "recommended_feature": "BREATHE", "action": {"type": "CONTINUE_FLOW", "feature": "BREATHE", "flow": "breathing"}}
    except Exception as e:
        print(f"Unified Response Error: {e}")
        return None

async def extract_name_from_memories(memories: list):
    """Identifies the user's name from past conversation context"""
    if not memories:
        return None
        
    try:
        system_prompt = """
        Review the following past conversation snippets and extract the user's name if they mentioned it.
        Return ONLY a JSON object with the key "name". If no name is found, return {"name": null}.
        Example: {"name": "Alex"}
        """
        
        user_message = "\n".join(memories)
        response_content = await run_classification(system_prompt, user_message)
        
        if not response_content:
            return None
            
        result = json.loads(response_content)
        return result.get("name")
    except Exception as e:
        print(f"Name Extraction Error: {e}")
        return None
