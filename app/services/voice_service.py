from app.services.openai_service import client
import os

def speech_to_text(audio_file_path: str):
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

def text_to_speech(text: str, output_path: str, voice: str = "nova"):
    """
    Available voices: alloy, echo, fable, onyx, nova, shimmer
    nova/shimmer are generally more empathetic/calm.
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
