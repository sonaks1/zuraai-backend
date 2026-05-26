import random

# Therapeutic Activity Engine - Standardized for ZuraAI
ACTIVITIES = {
    "stress": [
        {"id": "breathing", "label": "Breathing Exercise", "type": "FLOW", "description": "A mindful minute to find your center."},
        {"id": "grounding", "label": "Grounding Activity", "type": "FLOW", "description": "Reconnect with the present moment."},
        {"id": "calming_audio", "label": "Calm Audio", "type": "MEDIA", "description": "Soothing sounds for a busy mind."}
    ],
    "sadness": [
        {"id": "journaling", "label": "Guided Journal", "type": "FEATURE", "description": "Putting feelings into words can help."},
        {"id": "gratitude", "label": "Gratitude Reflection", "type": "FEATURE", "description": "Finding small anchors of light."},
        {"id": "reflection", "label": "Emotional Reflection", "type": "FLOW", "description": "A gentle space to sit with your feelings."}
    ],
    "anxiety": [
        {"id": "grounding", "label": "Grounding Exercise", "type": "FLOW", "description": "Bring your focus back to the 'now'."},
        {"id": "panic_relief", "label": "Panic Relief", "type": "MEDIA", "description": "Immediate support for intense moments."},
        {"id": "breathing", "label": "Slow Breathing", "type": "FLOW", "description": "Gently calm your nervous system."}
    ],
    "burnout": [
        {"id": "rest_audit", "label": "Rest Audit", "type": "FEATURE", "description": "Identify what kind of rest you need."},
        {"id": "stillness", "label": "Moment of Stillness", "type": "FLOW", "description": "Permission to just 'be' for a minute."},
        {"id": "calming_audio", "label": "Nature Sounds", "type": "MEDIA", "description": "Escape to a peaceful digital landscape."}
    ],
    "loneliness": [
        {"id": "gratitude", "label": "Gratitude Practice", "type": "FEATURE", "description": "Connecting with what matters to you."},
        {"id": "talking", "label": "Heart-to-Heart", "type": "FLOW", "description": "I'm right here to listen."},
        {"id": "check_in", "label": "Self-Compassion", "type": "FEATURE", "description": "A kind check-in with yourself."}
    ],
    "hopelessness": [
        {"id": "anchor", "label": "Small Anchor", "type": "FEATURE", "description": "Finding one tiny thing to hold onto."},
        {"id": "professional_help", "label": "Expert Support", "type": "FEATURE", "description": "Connect with someone who can help."},
        {"id": "breathing", "label": "Calm Breath", "type": "FLOW", "description": "Focusing on the very next breath."}
    ]
}

RECOMMENDATION_PROMPTS = {
    "stress": "It sounds like your mind has been carrying a lot. We can try a small grounding exercise together if you'd like. Sometimes it helps bring a little calm back into the moment.",
    "sadness": "Sometimes putting feelings into words can help a little. Would you like to try a short guided journal activity together?",
    "anxiety": "I'm right here with you. Let's try to find a little steadiness together. Would a grounding exercise or some slow breathing feel helpful right now?",
    "panic": "I'm right here. Let’s slow things down together for a moment. Would you like to try a calming exercise with me?",
    "loneliness": "I'm here, and I'm listening. Sometimes focusing on a small positive reflection can make things feel a little less heavy. Would you like to try that?",
    "neutral": "I'm here to support you. Would you like to try a wellness activity together, or just chat for a bit?"
}

WELLNESS_FLOWS = {
    "breathing": [
        "Okay. Slowly breathe in with me…",
        "Hold it gently for a second.",
        "Now slowly breathe out.",
        "Good job. Let your shoulders relax.",
        "Let's do one more slow breath together.",
        "Take a moment to notice how your breathing feels now. Does your body feel even a little lighter?",
        "You did really well. I'm right here if you need anything else."
    ],
    "compact_breathing": [
        "Let’s slow things down together. Take a deep breath in, hold it softly for a second, and slowly breathe out. Repeat this gently 3 times.",
        "Take your time. I’ll stay right here while you try it.",
        "That was a good step. How are you feeling now?"
    ],
    "grounding": [
        "Let's try to ground ourselves. Can you name 3 things you see right now?",
        "Good. Now, name 2 things you can feel, like the chair or your hands.",
        "And 1 thing you can hear?",
        "Take a slow breath. Notice the weight of your body where you're sitting. You're here, and you're safe.",
        "Even small pauses like this can help. How are you feeling now?"
    ],
    "sadness_support": [
        "I'm here with you. Say as much or as little as you'd like.",
        "Take your time. I'm here to listen.",
        "You don’t have to rush. Share whatever feels comfortable."
    ]
}

SUPPORTIVE_PHRASES = {
    "positive_reinforcement": [
        "That was a good step.",
        "I’m glad you stayed with it.",
        "Even small pauses like this can help.",
        "You handled that gently.",
        "That’s a positive step.",
        "You did really well.",
        "I'm proud of you for taking this moment."
    ],
    "acknowledgment": [
        "I hear you.",
        "I’m right here with you.",
        "It’s okay to feel this way.",
        "Thank you for sharing that with me.",
        "I’m listening."
    ],
    "relief": [
        "I’m glad things feel a little lighter right now.",
        "That’s good to hear. Take that feeling with you.",
        "I'm happy you're feeling a bit better.",
        "It sounds like a small weight has been lifted."
    ]
}

def get_random_support(category: str):
    return random.choice(SUPPORTIVE_PHRASES.get(category, ["I'm here for you."]))

def get_next_flow_step(flow_name: str, current_step: int):
    flow = WELLNESS_FLOWS.get(flow_name)
    if not flow or current_step >= len(flow):
        return None
    return flow[current_step]

def get_therapeutic_recommendation(emotion: str):
    emotion = emotion.lower()
    activities = ACTIVITIES.get(emotion, [
        {"id": "breathing", "label": "Gentle Breathing", "type": "FLOW", "description": "A quick pause for your breath."},
        {"id": "journaling", "label": "Daily Journal", "type": "FEATURE", "description": "Reflect on your day."}
    ])
    
    prompt = RECOMMENDATION_PROMPTS.get(emotion, RECOMMENDATION_PROMPTS["neutral"])
    
    return {
        "prompt": prompt,
        "activities": activities
    }
