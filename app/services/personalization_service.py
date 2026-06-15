def personality_mode(emotion: str):
    mapping = {
        "panic": "extremely_calm",
        "stress": "supportive",
        "sadness": "emotionally_warm",
        "anxiety": "gentle_reassurance",
        "burnout": "validating_rest",
        "emotional exhaustion": "validating_rest",
        "loneliness": "companionship_focused",
        "overthinking": "grounding_perspective",
        "emotional overload": "gentle_de-escalation",
        "fear": "protective_calm",
        "anger": "empathetic_listening",
        "hopelessness": "deep_validation"
    }
    return mapping.get(emotion.lower(), "balanced")

def get_personalized_prompt_extension(user_name: str = None, insights: dict = None, wellness_count: int = 0, user_profile: dict = None):
    """Generates a small prompt snippet for personalization based on long-term memory and structured profile"""
    context = ""
    
    # Filter out generic names
    generic_names = ["user", "app user", "friend", "guest", "none", "test user", "there"]
    is_generic = not user_name or user_name.lower().strip() in generic_names
    
    if user_name and not is_generic:
        context += f"The user's name is {user_name}. IMPORTANT: Do NOT use their name proactively in greetings or conversation unless they specifically ask 'what is my name?' or are introducing themselves.\n"
        context += f"USER STATUS: Name is KNOWN ({user_name}).\n"
    else:
        context += "The user's name is not yet known. Speak to them warmly without using a name until they provide it.\n"
        context += "USER STATUS: Name is UNKNOWN.\n"
    
    if user_profile:
        tier = user_profile.get("tier")
        layer = user_profile.get("onboarding_layer")
        pref = user_profile.get("support_preference")
        
        if tier:
            context += f"USER TIER: {tier}. (Psychiatric/Psychological need clinical empathy; Premium needs concierge-level care; Non-clinical is wellness-focused).\n"
        if layer:
            context += f"PRIMARY FOCUS: {layer}.\n"
        if pref:
            context += f"SUPPORT PREFERENCE: {pref}.\n"
    
    if insights:
        trend = insights.get("trend", "stable")
        triggers = insights.get("top_triggers", [])
        past_moods = insights.get("recent_emotions", [])
        
        if trend == "improving":
            context += "The user's mood has been improving recently. Acknowledge their progress and resilience.\n"
        elif trend == "declining":
            context += "The user has been struggling more than usual lately. Be extra patient and supportive.\n"
            
        if triggers:
            context += f"RECURRING STRESSORS: {', '.join(triggers)}. If they mention these, show you remember they've come up before.\n"
            
        if past_moods:
            context += f"HISTORICAL CONTEXT: The user has previously expressed feeling {', '.join(past_moods[:3])}. IMPORTANT: This is for background only. Do NOT assume they feel this way right now unless they say so in their current message.\n"
            
    if wellness_count > 0:
        context += f"WELLNESS PROGRESS: They've completed {wellness_count} wellness exercises this week.\n"
        
    return context