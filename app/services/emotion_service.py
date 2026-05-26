from app.services.openai_service import run_classification
import json

async def detect_emotion(message: str):
    try:
        system_prompt = "You are an emotional intelligence engine. Analyze the emotional state and identify the primary emotion from this list: Anxiety, Stress, Sadness, Panic, Loneliness, Burnout, Hopelessness, Neutral. Also provide a severity score between 0.0 and 1.0. Return ONLY a JSON object with keys 'emotion' and 'severity'."
        
        response_content = await run_classification(system_prompt, message)
        if not response_content:
            raise Exception("Empty classification response")
            
        result = json.loads(response_content)
        return {
            "emotion": result.get("emotion", "neutral").lower(),
            "severity": float(result.get("severity", 0.2))
        }

    except Exception as e:
        print(f"Emotion Detection Error: {e}")
        # Fallback to basic keyword matching if AI fails
        text = message.lower()
        if "stress" in text: return {"emotion": "stress", "severity": 0.7}
        if "panic" in text: return {"emotion": "panic", "severity": 0.9}
        return {"emotion": "neutral", "severity": 0.2}