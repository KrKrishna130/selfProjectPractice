from io import BytesIO
from gtts import gTTS

# yaha text to speech  de rahe hai

class TextToSpeech:
    def speak(self, text, lang="en"):
        cleaned = (text or "").strip()

        if not cleaned:
            return
        
        buffer = BytesIO()
        
# yaha hm gtts me text passed krte hai
        gTTS(text=cleaned, lang=lang).write_to_fp(buffer)

        buffer.seek(0)

        return buffer.read()
    