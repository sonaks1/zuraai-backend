# Standardized Feature Names for Mibo Frontend
FEATURE_MAP = {
    "BREATHE": ["stress help", "panic help", "calming exercises", "breathing", "breathe", "slow breath"],
    "BOX_BREATHE": ["box breathing", "square breathing", "4-4-4-4"],
    "478_BREATHE": ["4-7-8", "478 breathing", "deep relaxation breath"],
    "GROUNDING": ["grounding", "5-4-3-2-1", "present moment", "object awareness"],
    "CBT_REFRAME": ["thought reframing", "look at it differently", "negative thoughts", "reframe"],
    "BODY_SCAN": ["body scan", "tension in body", "physical relaxation"],
    "TENSION_RELEASE": ["tension release", "muscle relaxation", "squeeze and release"],
    "JOURNAL": ["write thoughts", "express feelings", "reflect emotionally", "journaling", "journal"],
    "GRATITUDE": ["emotionally negative", "hopeless", "disconnected", "gratitude", "thankful"],
    "INSIGHTS": ["How have I been feeling recently?", "Track my emotions", "analytics", "patterns", "insights"],
    "THERAPIST_BOOKING": ["therapist", "psychologist", "psychiatrist", "counseling", "professional help", "booking"],
    "INSTANT_SUPPORT": ["crisis", "panic", "emotional breakdown", "self-harm", "suicidal", "emergency"],
    "ASSESSMENT": ["test", "assessment", "checkup", "stress test", "anxiety test", "depression test", "sleep test", "burnout test", "how stressed am i", "check my anxiety", "mood check"]
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

    # 2. Assessment Routing
    assessment_keywords = {
        "stress": ["stress test", "how stressed am i", "stress assessment", "stress check", "assessment"],
        "anxiety": ["anxiety test", "check my anxiety", "anxiety assessment", "anxiety check"],
        "depression": ["depression test", "mood check", "depression assessment", "mood assessment"],
        "sleep": ["sleep test", "sleep assessment", "check my sleep", "sleep check"],
        "burnout": ["burnout test", "burnout assessment", "burnout check"],
        "onboarding": ["onboarding", "intake", "check-in", "first-time", "get started", "questionnaire"]
    }
    
    # Check intent first
    for assessment_type, keywords in assessment_keywords.items():
        if any(kw in intent_lower for kw in keywords):
            return {
                "recommended_feature": "ASSESSMENT",
                "action": {
                    "type": "START_ASSESSMENT",
                    "feature": "ASSESSMENT",
                    "assessment_type": assessment_type
                }
            }

    # If intent is generic "Assessment", use emotion as a fallback
    if intent_lower == "assessment":
        assessment_type = "stress" # Default
        if emotion in assessment_keywords:
            assessment_type = emotion
        
        return {
            "recommended_feature": "ASSESSMENT",
            "action": {
                "type": "START_ASSESSMENT",
                "feature": "ASSESSMENT",
                "assessment_type": assessment_type
            }
        }

    # 3. Overwhelmed / Panic Relief (Media Flow)
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