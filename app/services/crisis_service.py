from app.services.openai_service import run_classification
import json

async def detect_crisis(message: str):
    try:
        system_prompt = """
        You are a specialized Crisis & Safety Assessment Engine. Analyze the following user message for specific indicators of emotional distress or safety risks.

        RISK LEVELS & CRITERIA:
        - MILD (Level 1): Mentions of daily stress, work pressure, or minor mood fluctuations. No safety risk.
        - MODERATE (Level 2): Persistent sadness, anxiety symptoms, emotional instability, or signs of burnout.
        - CRITICAL (Level 3): Indicators of self-harm, suicidal thoughts, or severe emotional crisis.

        Return ONLY a JSON object:
        {
          "level": "Mild/Moderate/Critical/None",
          "risk_score": 0.0-1.0,
          "is_critical": true/false,
          "reason": "specific reason for this classification"
        }
        """

        response_content = await run_classification(system_prompt, message)
        if not response_content:
            raise Exception("Empty classification response")

        result = json.loads(response_content)
        level_str = result.get("level", "None").lower()
        
        # Standardize risk levels
        risk_level = "low"
        if level_str == "moderate": risk_level = "moderate"
        if level_str == "critical": risk_level = "critical"
        
        return {
            "risk_level": risk_level,
            "critical": risk_level == "critical",
            "reason": result.get("reason", ""),
            "severity_label": result.get("level", "None")
        }

    except Exception as e:
        print(f"Crisis Detection Error: {e}")
        # Fallback
        return {"risk_level": "low", "critical": False, "reason": "Fallback", "severity_label": "None"}