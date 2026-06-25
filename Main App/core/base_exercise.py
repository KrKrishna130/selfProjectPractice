import math 
from abc import ABC, abstractmethod

# here we write base exercise class.it is detector class isko bad me implement krgenge call krk
# Mediapipe Model concept apply here
# yaha pr hm jo likhnge usse face pr landmark etc dikhega detect krega(squat,push up,Biecep,...etc)

class BaseExercise(ABC):
    def __init__(self):
        self.reps = 0
        self.stage = None

# body movement(exercise) k time angle calculate k k liye used hoga
# dumble me elbow angle 90 hai to rep complete one count hoga nii to complte nii hua hai
# ye rep count me help krega
# yaha hm vector dot formula se angle calculate kr rahe hai
# u.v=|u|v||.cos0-->angle(cos0)= u.v/(|u|v||)

    def calculate_angle(self, a, b, c):
        ax, ay = a[0] - b[0], a[1] - b[1]
        cx, cy = c[0] - b[0], c[1] - b[1]

        dot = ax * cx + ay * cy

        mag_a = math.sqrt(ax ** 2 + ay ** 2)
        mag_c = math.sqrt(cx ** 2 + cy ** 2)

# agar ye zero hoga to error aa  jaega isliye condition dal de rahe hai
# taki niche divide hoga to error nii aayega
        if mag_a * mag_c == 0:
            return 0.0
        
# fina angle usimg acos (arc cos formula)
# yaha (-1 ,1 ) iske beech k value lana hai
        cos_angle = max(-1.0, min(1.0, dot / (mag_a * mag_c)))

        return math.degrees(math.acos(cos_angle))
    
# yaha point get krega ye method body pr landmark k liye

    def get_point(self, landmarks, idx):
        p = landmarks[idx]

        return (p.x, p.y)
    
# yaha hmne ek abstract method denge taki process krte time media used hoga,and landmark detect krega
    @abstractmethod
    def process(self, landmarks):
        pass


    @abstractmethod
    def reset(self):
        pass
