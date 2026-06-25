import time
import streamlit as st

# yaha hme texttospeech tts and llm ko import krk uska method used krte hai
# yaha hm voice initiative k liye pura configuration krenge
class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
# yaha hm isse k liye form hai-exercise de rahe hai,metrics k sath
    def _find_form_issue(self, exercise, metrics):
        if "issue" in metrics:
            return metrics["issue"]
        
# yaha exercise wise data de rahe hai
        if exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)
            
            if depth == "TOO HIGH":
                return "The user's squat is not deep enough — knees are not bending sufficiently."

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "The user is leaning too far forward during the squat."

        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")
            
            if alignment == "Poor Form":
                return "The user's body is not straight during the push-up."

            if hip_status == "SAGGING":
                return "The user's hips are sagging down during the push-up."

            if hip_status == "PIKED UP":
                return "The user's hips are too high — lower them to form a straight line."

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")
            
            if swing == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."

        elif exercise == "Shoulder Press":
            back_arch = metrics.get("back_arch_status", "")
            extension = metrics.get("extension_status", "")
            
            if back_arch == "Excessive Arch":
                return "The user is arching their lower back excessively during the press."

            if back_arch == "Slight Arch":
                return "Slight back arch detected — encourage the user to brace their core."

        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")
            
            if balance == "OFF BALANCE":
                return "The user is losing balance during the lunge — feet should be hip-width apart."

        return None

# yaha hm event process voice k liye dnege
    def process_event(self, event, exercise, metrics):
        issue = self._find_form_issue(exercise, metrics)

        now = time.time()
# agar in 3 me  se ki hai to bhej deneg other wise none bhej denge
        is_major_issue = event in ["workout_started", "set_completed", "workout_completed"]

        if not is_major_issue:
            if not issue:
                return None
            # yaha hm do issue k beech me 5 sec ki gap rakhenge taki user exp better rahega
            if now - self.last_spoken_at < 5:
                return None
            # yaha hm llm k jariye iisue bhej denge
        text = self.llm.give_feedback(event, issue)

        # llm se jo text aaya usko hm speech me convert krk response bhej dnege
        voice = self.tts.speak(text)

        self.last_spoken_at = now
# voice hm user ko sunayenge and text bhi used kr leneg response k liye
        return voice, text
    

def autoplay_audio(audio_bytes):
    if not audio_bytes:
        return
    
    st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
    
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
