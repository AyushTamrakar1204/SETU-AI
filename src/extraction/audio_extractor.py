import os
from openai import OpenAI

def transcribe_site_audio(audio_file_obj, language_code="en"):
    """
    Transcribes or translates site supervisor audio notes using OpenAI Whisper.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[Error: OPENAI_API_KEY not found in environment variables]"
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Save temporary file from Streamlit's audio buffer
        temp_path = "temp_voice_note.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_file_obj.getbuffer())
        
        with open(temp_path, "rb") as audio_file:
            if language_code == "en":
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            else:
                # Whisper translation endpoint translates any spoken language to English text
                transcript = client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file
                )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return transcript.text
    except Exception as e:
        return f"[Transcription Error: {str(e)}]"