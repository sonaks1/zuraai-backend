# Standardized Feature Names for Mibo Frontend
FEATURE_MAP = {
    "BREATHE": ["stress help", "panic help", "calming exercises", "breathing", "breathe"],
    "JOURNAL": ["write thoughts", "express feelings", "reflect emotionally", "journaling", "journal"],
    "GRATITUDE": ["emotionally negative", "hopeless", "disconnected", "gratitude"],
    "INSIGHTS": ["How have I been feeling recently?", "Track my emotions", "analytics", "patterns", "insights"],
    "THERAPIST_BOOKING": ["therapist", "psychologist", "psychiatrist", "counseling", "professional help", "booking"],
    "INSTANT_SUPPORT": ["crisis", "panic", "emotional breakdown", "self-harm", "suicidal", "emergency"]
}

def route_action(intent: str, emotion: str, risk_level: str = "low"):
    intent_lower = intent.lower()
    
    # 1. Crisis Handling (Emergency)
    if risk_level == "critical" or "Instant Emotional Support" in intent:
        return {
            "recommended_feature": "INSTANT_SUPPORT",
            "action": {
                "type": "EMERGENCY_SUPPORT",
                "feature": "INSTANT_SUPPORT"
            }
        }

    # 2. Overwhelmed / Panic Relief (Media Flow)
    if "overwhelmed" in intent_lower or "panic" in intent_lower:
        return {
            "recommended_feature": "BREATHE",
            "action": {
                "type": "OPEN_WELLNESS_MEDIA",
                "feature": "BREATHE",
                "media_id": "panic_relief_01"
            }
        }

    # 3. Therapist Escalation
    if "Therapist" in intent or emotion == "hopelessness":
        return {
            "recommended_feature": "THERAPIST_BOOKING",
            "action": {
                "type": "THERAPIST_ESCALATION",
                "feature": "THERAPIST_BOOKING"
            }
        }

    # 3. Intelligent Feature Routing
    for feature, keywords in FEATURE_MAP.items():
        if any(kw.lower() in intent_lower for kw in keywords):
            return {
                "recommended_feature": feature,
                "action": {
                    "type": "OPEN_FEATURE",
                    "feature": feature
                }
            }

    # Default: No specific feature action
    return {
        "recommended_feature": "ZURAAI_CHAT",
        "action": {
            "type": "OPEN_FEATURE",
            "feature": "ZURAAI_CHAT"
        }
    }