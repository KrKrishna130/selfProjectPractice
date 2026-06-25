from core.base_exercise import BaseExercise
# BaseExercise ko implemnt krte hai import krk 
# yaha hm  sare excercise hai unko implement one by one krte hai

# yaha only squat k liye logic denge

# yaha hm inherit kr rahe hai BaseExercise class ko
class SquatDetector(BaseExercise):
# yahi sara process and logic same implemnet krne honge sare exercise me
    # yaha sara constant variables de denge

    DOWN_THRESHOLD = 100   
    UP_THRESHOLD = 160     
    MIN_VISIBILITY = 0.7

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

# yaha hme dono legs k aur dono knees angle find krenge aur dekhenge 
# jiski jayada visibility rahega usko consider krgene

    def process(self, landmarks):
        # iske andar sare constant langege
        # knees angle calculate
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE)
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE)
        )
# yaha visibility check krgenge
        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility
# yaha logic dnege
        if left_vis >= right_vis:
            knee_angle = left_knee_angle
            # yaha index sare denge jiska jyada visibility tha uska consider kr leneg index uska wala used hoga aage
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE, self.LEFT_SHOULDER
        else:
            knee_angle = right_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE, self.RIGHT_SHOULDER

# yaha hm back angle find krenge 

        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )

        key_landmark_visible = landmarks[hip_idx].visibility >= self.MIN_VISIBILITY and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY

# agar jo jyada hai upar me assign kr hi diye hai

        if key_landmark_visible:
            # yaha visibility hai uska angle check kr rahe hai 
            # agar DOWN_THRESHOLD se knee_angle km hai down stage define kr rahe hai
            if knee_angle < self.DOWN_THRESHOLD:
                self.stage = "down"
  # agar UP_THRESHOLD se knee_angle jyda hai up stage define kr rahe hai to finally reps +1 hoga count
            if knee_angle >= self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        if self.stage == "down":
            depth_status = "GOOD DEPTH" if knee_angle <= self.DOWN_THRESHOLD else "TOO HIGH"
        elif self.stage == "up":
            depth_status = "STANDING"
        else:
            depth_status = "N/A"
#  yaha dictionary return kr denge
        return {
            "reps": self.reps,
            "knee_angle": int(knee_angle),
            "back_angle": int(back_angle),
            "depth_status": depth_status
        }
    