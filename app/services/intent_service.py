from app.services.openai_service import run_classification
import json

async def detect_intent(message: str):
    try:
        system_prompt = """
        Determine the user's intent from this list:
        - Breathe (Breathing/calming/stress help)
        - Journal (Writing thoughts/reflecting)
        - Gratitude (Positive reflection/negative feelings help)
        - Insights (Emotion tracking/analytics/How have I been feeling?)
        - Therapist Booking (Counseling/Psychologist/Professional help)
        - Instant Emotional Support (Emergency/Crisis/Panic)
        - General chat
        Return ONLY a JSON object with keys "intent" and "confidence" (0.0 to 1.0).
        """

        response_content = await run_classification(system_prompt, message)
        if not response_content:
            raise Exception("Empty classification response")
            
        result = json.loads(response_content)
        return {
            "intent": result.get("intent", "General chat"),
            "confidence": float(result.get("confidence", 1.0))
        }

    except Exception as e:
        print(f"Intent Detection Error: {e}")
        return {
            "intent": "General chat",
            "confidence": 0.0
        }

