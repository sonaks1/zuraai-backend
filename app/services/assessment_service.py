from typing import List, Dict, Any

ASSESSMENTS = {
    "stress": {
        "title": "Stress Assessment",
        "questions": [
            "How often have you felt overwhelmed in the last 2 weeks? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "How often have you found it difficult to relax? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "How often have you felt unable to control important things in your life? (0: Never, 1: Sometimes, 2: Often, 3: Always)"
        ],
        "thresholds": [
            {"max": 3, "label": "Low Stress"},
            {"max": 6, "label": "Moderate Stress"},
            {"max": 9, "label": "High Stress"}
        ]
    },
    "anxiety": {
        "title": "Anxiety Assessment",
        "questions": [
            "Feeling nervous or anxious? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Unable to stop worrying? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Trouble relaxing? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Becoming easily irritated? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)"
        ],
        "thresholds": [
            {"max": 4, "label": "Minimal Anxiety"},
            {"max": 8, "label": "Mild Anxiety"},
            {"max": 12, "label": "Moderate Anxiety"},
            {"max": 15, "label": "Severe Anxiety"}
        ]
    },
    "depression": {
        "title": "Depression / Mood Assessment",
        "questions": [
            "Little interest or pleasure in activities? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Feeling down, depressed, or hopeless? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Low energy? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)",
            "Trouble concentrating? (0: Not at all, 1: Several days, 2: More than half the days, 3: Nearly every day)"
        ],
        "thresholds": [
            {"max": 4, "label": "Minimal Depression"},
            {"max": 8, "label": "Mild Depression"},
            {"max": 12, "label": "Moderate Depression"},
            {"max": 15, "label": "Severe Depression"}
        ]
    },
    "sleep": {
        "title": "Sleep Quality Assessment",
        "questions": [
            "How many hours do you sleep? (0: 7-9 hours, 1: 6-7 hours, 2: 5-6 hours, 3: Less than 5 hours)",
            "Difficulty falling asleep? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "Waking up during the night? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "Feeling rested in the morning? (3: Never, 2: Sometimes, 1: Often, 0: Always)"
        ],
        "thresholds": [
            {"max": 4, "label": "Healthy Sleep"},
            {"max": 8, "label": "Mild Sleep Difficulty"},
            {"max": 12, "label": "Significant Sleep Difficulty"}
        ]
    },
    "burnout": {
        "title": "Burnout Assessment",
        "questions": [
            "Feeling emotionally exhausted? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "Feeling drained after work? (0: Never, 1: Sometimes, 2: Often, 3: Always)",
            "Difficulty staying motivated? (0: Never, 1: Sometimes, 2: Often, 3: Always)"
        ],
        "thresholds": [
            {"max": 3, "label": "Low Burnout"},
            {"max": 6, "label": "Moderate Burnout"},
            {"max": 9, "label": "High Burnout"}
        ]
    },
    "onboarding": {
        "title": "Mibo Onboarding",
        "questions": [
            "What brings you here?\nA. Going through something rn, need to talk\nB. Been struggling a while, want real help\nC. I’m okay, just wanna feel better or grow\nD. Want something private and low-key",
            "How have the last 2 weeks felt?\nA. Mostly fine\nB. Stressed or low sometimes\nC. Heavy most days\nD. Not okay — I need help soon",
            "Noticed any changes in your sleep, appetite, or how safe you feel? (Be honest with this one — it stays private.)\nA. Not really\nB. A little off\nC. Yes, pretty noticeable\nD. I’ve had thoughts of harming myself or don’t feel safe",
            "How soon do you want to start?\nA. Just looking around\nB. This week-ish\nC. As soon as possible\nD. Right now — it’s urgent",
            "What are you most drawn to?\nA. Talking to a pro — therapist or psychiatrist\nB. Calm stuff — sleep, mood, meditation\nC. Learning & growth — courses, self-understanding\nD. Private or specialised care",
            "When it comes to opening up?\nA. I’m an open book\nB. Need to trust you first\nC. Privacy is everything to me\nD. Hard to talk — I prefer going slow or texting",
            "Who’s this for?\nA. Me\nB. My kid or teen\nC. Someone I care about\nD. My team or workplace"
        ],
        "thresholds": [] # Onboarding uses custom routing logic
    }
}

def calculate_onboarding_route(answers: List[str]) -> Dict[str, Any]:
    """
    Calculates the routing path based on 7 answers (A, B, C, D).
    Returns a dict with tier, layer, tags, and privacy settings.
    """
    if len(answers) < 7:
        return {"tier": "incomplete"}

    q1, q2, q3, q4, q5, q6, q7 = [a.upper() for a in answers]

    # 1. Emergency Check (Q3-D)
    if q3 == 'D':
        return {"tier": "EMERGENCY", "action": "trigger_crisis_protocol"}

    # Interest & Privacy Mapping
    interests = {
        'A': 'Clinical',
        'B': 'Sleep/Mood/Meditation',
        'C': 'Courses/Growth',
        'D': 'Premium/Specialized'
    }
    privacy = {
        'A': 'Open',
        'B': 'Trust-first',
        'C': 'Privacy-focused',
        'D': 'Text-only/Slow'
    }

    results = {
        "tier": "Non-clinical",
        "layer": _get_layer(q7),
        "interest_tags": interests.get(q5, 'General'),
        "privacy_preference": privacy.get(q6, 'Standard')
    }

    # 2. Severity Signals (Psychiatric) - Outranks everything
    is_high_severity = q2 in ['C', 'D'] or q3 == 'C' or q4 == 'D'
    if is_high_severity:
        results["tier"] = "Psychiatric"
        results["description"] = "Clinical assessment and possible medication support."
        return results

    # 3. Psychological Signal
    is_psychological = q1 == 'B' or q5 == 'A' or q4 == 'C'
    if is_psychological:
        results["tier"] = "Psychological"
        results["description"] = "Therapy and counseling support."
        return results

    # 4. Premium Signal
    is_premium = q1 == 'D' or q5 == 'D' or q6 == 'C'
    if is_premium:
        results["tier"] = "Premium"
        results["description"] = "Private, concierge-level care — The Prime Project."
        return results

    # 5. Default: Non-clinical
    results["description"] = "Mindfulness, sleep, mood, courses, and habits."
    return results

def _get_layer(q7_answer: str) -> str:
    layers = {
        'A': 'Mibo Main',
        'B': 'MiboKids / Teens',
        'C': 'Couples & Family',
        'D': 'Mibo Workplace OS'
    }
    return layers.get(q7_answer, 'Mibo Main')

def get_assessment_result(assessment_type: str, total_score: int, answers: List[str] = None) -> str:
    if assessment_type == "onboarding" and answers:
        route = calculate_onboarding_route(answers)
        return f"{route['tier']} ({route.get('description', '')})"
    
    assessment = ASSESSMENTS.get(assessment_type)
    if not assessment:
        return "Unknown"
    
    for threshold in assessment["thresholds"]:
        if total_score <= threshold["max"]:
            return threshold["label"]
    
    return assessment["thresholds"][-1]["label"]

def get_assessment_question(assessment_type: str, step: int) -> str:
    assessment = ASSESSMENTS.get(assessment_type)
    if not assessment or step >= len(assessment["questions"]):
        return None
    return assessment["questions"][step]

def is_assessment_finished(assessment_type: str, step: int) -> bool:
    assessment = ASSESSMENTS.get(assessment_type)
    if not assessment:
        return True
    return step >= len(assessment["questions"])
