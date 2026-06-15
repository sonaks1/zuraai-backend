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
    audio_metadata: dict = None,
    personality: str = "warm"
):
    try:
        memory_context = "\nPAST: " + "; ".join(memories) if memories else ""
        history_context = ""
        if history:
            history_context = "\nLAST 3:\n" + "\n".join([f"U: {c.message}\nA: {c.response}" for c in reversed(history[:3])])
        
        system_prompt = f"""
You are ZuraAI, a warm and professional wellness companion. Your goal is to provide directive coaching with deep empathy and expert-level synthesis.

MISSING NAME RULE:
- If the user's name is unknown (None or empty), your HIGHEST PRIORITY is to ask for it warmly.
- Example: "Hi there. Before we begin, what would you like me to call you?"
- Once they provide a name, acknowledge it and proceed with the conversation.

NAME USAGE RULE: 
- DO NOT use the user's name in greetings or throughout the chat proactively once known. 
- ONLY use their name if they specifically ask "what is my name?" or if they are introducing themselves for the first time.
- Address them warmly (e.g., "I'm here for you", "Let's work through this together") without using a name.

RECOGNITION & SYNTHESIS RULES:
1. Synthesize Context: If the user provides new info (e.g., "periods" after "pain"), acknowledge the connection immediately.
2. Practical Care First: For sadness, crying, or physical discomfort, prioritize practical self-care (rest, hydration, warmth) and emotional check-ins before suggesting structured exercises.
3. Exercise Relevance: 
   - FOR ANXIETY/PANIC: Use 'grounding' or 'breathing'.
   - FOR SADNESS/OVERWHELM: Use 'reflection_flow', 'self_esteem', or 'thought_reframing'. AVOID 'grounding' unless they feel disconnected.
4. Directive Initiative: Take initiative with 1-2 small relaxation steps. Evolve these steps each turn; do not repeat.
5. Smooth Transitions: Before suggesting a flow, validate the user's current state. If they just "ok'd" a small step, acknowledge it ("Thank you for trying that...") before moving to a structured flow.
6. Professional Depth: For sadness/crying, ask about the specific quality of the feeling (e.g., "Does it feel like exhaustion, loneliness, or just a heavy mix of everything?") to show deep listening.
7. Exercise Ineffectiveness: If the user says an exercise didn't work or they feel "no changes", acknowledge it warmly and IMMEDIATELY suggest a DIFFERENT technique from the list below. Do not ask "would you like to try something else?" without naming what it is.

{personalized_context}
{memory_context}
{history_context}

Return ONLY JSON:
{{
  "analysis": {{
    "emotion": "...", 
    "severity_score": 0.0, 
    "severity_level": "Mild/Moderate/Critical",
    "risk_level": "low/moderate/critical", 
    "intent": "...", 
    "triggers": [], 
    "name": "..."
  }},
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
        data = json.loads(response.choices[0].message.content)
        
        # Ensure severity_level is present in analysis for compatibility
        if "analysis" in data and "severity_level" not in data["analysis"]:
            score = data["analysis"].get("severity_score", 0.2)
            if score >= 0.9: data["analysis"]["severity_level"] = "Critical"
            elif score >= 0.6: data["analysis"]["severity_level"] = "Moderate"
            else: data["analysis"]["severity_level"] = "Mild"
            
        return data
    except RateLimitError:
        return {"analysis": {"emotion": "neutral", "severity_score": 0.2, "severity_level": "Mild", "risk_level": "low", "intent": "chat"}, "reply": "I'm here for you, but I'm a bit overwhelmed right now. Let's take a slow breath together.", "suggested_flow": "breathing", "recommended_feature": "BREATHE", "action": {"type": "CONTINUE_FLOW", "feature": "BREATHE", "flow": "breathing"}}
    except Exception as e:
        print(f"Unified Response Error: {e}")
        return None

async def comprehensive_analysis(message: str, previous_emotion: str = None):
    """Compatibility wrapper for websocket_service.py"""
    result = await generate_unified_zura_response(message, previous_emotion=previous_emotion)
    if result and "analysis" in result:
        return result["analysis"]
    return None

async def generate_ai_response(**kwargs):
    """Compatibility alias for websocket_service.py"""
    return await generate_unified_zura_response(**kwargs)


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
