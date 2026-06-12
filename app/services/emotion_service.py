from app.services.openai_service import run_classification
import json

async def detect_emotion(message: str, audio_metadata: dict = None, previous_emotion: str = None):
    try:
        # Include audio metadata in analysis if provided
        audio_context = ""
        if audio_metadata:
            audio_context = f"\nAUDIO ANALYSIS:\n- Tone: {audio_metadata.get('tone')}\n- Speed: {audio_metadata.get('speed')}\n- Silence Patterns: {audio_metadata.get('silence')}"

        continuity_context = ""
        if previous_emotion:
            continuity_context = f"\nCONTINUITY:\n- The user was recently feeling: {previous_emotion}. Consider if the current message is a continuation of this state."

        system_prompt = f"""
You are an advanced Emotional Intelligence Engine. Analyze the user's input (text and optional audio data) to identify their primary emotional state and severity.

EMOTIONS TO DETECT:
- Stress
- Anxiety
- Sadness
- Fear
- Anger
- Loneliness
- Hopelessness
- Emotional Exhaustion (Burnout)
- Neutral
{continuity_context}

SEVERITY CLASSIFICATION:
1. MILD: Daily stress, work pressure, minor mood fluctuations.
2. MODERATE: Persistent sadness, anxiety symptoms, emotional instability.
3. CRITICAL: Severe emotional crisis, self-harm indicators, suicidal thoughts.

Analyze:
- Text content and sentiment.
- If the user is confused or "doesn't know what's happening," consider it a continuation of their previous state if it was high-intensity (e.g., Anger, Anxiety).
{audio_context if audio_metadata else "- (No audio metadata provided)"}

Return ONLY a JSON object:
{{
  "emotion": "primary_emotion",
  "severity_level": "Mild/Moderate/Critical",
  "severity_score": 0.0-1.0,
  "intensity": "low/medium/high",
  "reasoning": "brief explanation"
}}
"""
        
        response_content = await run_classification(system_prompt, message)
        if not response_content:
            raise Exception("Empty classification response")
            
        result = json.loads(response_content)
        return {
            "emotion": result.get("emotion", "neutral").lower(),
            "severity_level": result.get("severity_level", "Mild"),
            "severity": float(result.get("severity_score", 0.2)),
            "intensity": result.get("intensity", "low"),
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        print(f"Emotion Detection Error: {e}")
        # Fallback keyword matching
        text = message.lower()
        if any(word in text for word in ["die", "kill", "hurt myself", "end it"]):
            return {"emotion": "hopelessness", "severity_level": "Critical", "severity": 0.9}
        if "anger" in text or "angry" in text or "hate" in text:
            return {"emotion": "anger", "severity_level": "Moderate", "severity": 0.6}
        if "fear" in text or "scared" in text or "afraid" in text:
            return {"emotion": "fear", "severity_level": "Moderate", "severity": 0.6}
        if "exhausted" in text or "burnout" in text:
            return {"emotion": "emotional exhaustion", "severity_level": "Moderate", "severity": 0.7}
        return {"emotion": "neutral", "severity_level": "Mild", "severity": 0.2}