from app.services.openai_service import client
import os

async def speech_to_text(audio_file_path: str):
    try:
        with open(audio_file_path, "rb") as audio_file:
            # Using verbose_json to get segment data for speed and silence analysis
            response = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="verbose_json"
            )
        
        transcript_text = response.text
        segments = response.segments
        
        # Perform Audio Analysis
        analysis = analyze_audio_features(segments)
        
        return {
            "text": transcript_text,
            "analysis": analysis
        }
    except Exception as e:
        print(f"STT Error: {e}")
        return {"text": "", "analysis": None}

def analyze_audio_features(segments):
    """
    Analyzes speech speed and silence patterns from Whisper segments.
    """
    if not segments:
        return None
        
    total_duration = segments[-1].end - segments[0].start
    total_words = sum(len(s.text.split()) for s in segments)
    
    # Speech Speed (Words per minute)
    wpm = (total_words / total_duration) * 60 if total_duration > 0 else 0
    
    # Silence Patterns (Gaps between segments)
    silence_duration = 0
    for i in range(len(segments) - 1):
        gap = segments[i+1].start - segments[i].end
        if gap > 0.5: # Consider gaps > 0.5s as significant silence
            silence_duration += gap
            
    # Normalize speed
    speed_category = "normal"
    if wpm > 150: speed_category = "fast"
    elif wpm < 80: speed_category = "slow"
    
    return {
        "speed": speed_category,
        "wpm": round(wpm, 2),
        "silence_duration": round(silence_duration, 2),
        "silence_pattern": "frequent" if silence_duration > (total_duration * 0.2) else "minimal",
        "tone": "detected from text context" # Placeholder as pure audio tone requires different models
    }

import base64

async def text_to_speech(text: str, voice: str = "nova"):
    """
    Returns base64 encoded audio string directly to avoid disk I/O.
    """
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        # Get bytes directly from response
        audio_data = await response.aread()
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
