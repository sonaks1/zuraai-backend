from app.services.openai_service import run_classification
import json

async def detect_crisis(message: str):
    try:
        system_prompt = """
        You are a crisis and safety assessment engine. Analyze the following user message for potential crisis or emotional distress.
        Categorize the risk level into one of the following:
        - Level 1: Mild Distress
        - Level 2: Moderate Distress
        - Level 3: Critical Situation
        - None: No distress detected.
        Return ONLY a JSON object with keys "level" (1, 2, 3, or 0 for None) and "reason".
        """

        response_content = await run_classification(system_prompt, message)
        if not response_content:
            raise Exception("Empty classification response")

        result = json.loads(response_content)
        level_int = int(result.get("level", 0))
        
        # Mapping to standardized risk levels
        risk_map = {
            0: "low",
            1: "low",
            2: "moderate",
            3: "critical"
        }
        risk_level = risk_map.get(level_int, "low")
        
        return {
            "risk_level": risk_level,
            "critical": risk_level == "critical",
            "reason": result.get("reason", "")
        }

    except Exception as e:
        print(f"Crisis Detection Error: {e}")
        # Fallback
        return {"risk_level": "low", "critical": False, "reason": "Fallback"}