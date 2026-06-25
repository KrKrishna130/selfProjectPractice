import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector
from services.config.workout_config import POSE_CONNECTIONS

# yaha hm video processing ka logic sara denge 
# VideoProcessorBase ye webrtc k undar ka class inherit krk logic dnege

class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        # threading.Lock() used hoga thread safety k liye 
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"

# yaha Google dwara jo model bnaya gya hai -->>mediapipe model download kiye usko load krk 
# call krenge and uska sara features used krnege video processing k liye
# pose_landmarker_full.task ---->> ML model hai

        model_path = os.path.join(os.getcwd(), "ml_models", "pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path=model_path)

# mediapipe.tasks.python import vision k undar ka method me path dete hai ML model ka

        options = vision.PoseLandmarkerOptions(
            base_options=base_option,  # isme base_option upar wala dal denge
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            output_segmentation_masks=False
        )

        self._landmarker = vision.PoseLandmarker.create_from_options(options)

        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

        self._frame_timestamps_ms = 0

# jo variable upar me diye the un sab ka getter and setter method denge
    # lock ka set method hai
    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

 # lock ka get method hai
    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()
        
    def set_exercise(self, exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type
        
    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]

# POSE_CONNECTIONS  start Index and last index return krta hai

        for start_idx, end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]
# yaha visibility point1 and point 2 ka greater than 0.7 hoga tabhi
# cv2.line create krnge ,mtlb visibility clear cut dikhega tabhi line bnega body detect k liye
            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                    img, # skleton image rahega body rahega
                    (int(p1.x * w), int(p1.y * h)), # point1 ka location pass kr rahe hai
                    (int(p2.x * w), int(p2.y * h)), # point2 ka location pass kr rahe hai
                    (0, 255, 0), #yaha hm line ka colour green de rahe hai RGB value se
                    8  # yaha hm pixel ka line create hogi
                )
        # yaha hm dot jo create hota hai landamark me body pr usko de rahe hai
        for lm in landmarks: 
            if lm.visibility > 0.7: # if visibility greater than 0.7 hai tabhi
                cv2.circle(
                    img, # skleton image rahega body rahega
                    (int(lm.x * w), int(lm.y * h)), # yaha hm position de rahe hai hight
                    8,  # yaha radius de rahe hai
                    (255, 0, 0), # yaha colour
                    -1  # yaha pixel de rahe hai
                )
    # agar image clear nii hai body ka to ye message = NO POSE DETECTED dega 
    def _draw_no_pose_warnings(self, img):
        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
# yaha hm sara excercise ka type de dege uska method jo diye hai upar usko call kr leneg
    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)
        elif ex_type == "Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type == "Biceps Curls (Dumbbell)":
            self._draw_curl_overlays(img, metrics)
        elif ex_type == "Shoulder Press":
            self._draw_press_overlays(img, metrics)
        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)

# yaha _draw_squats_overlays k liye method bna diye hai
    def _draw_squats_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"DEPTH: {metrics['depth_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
    # yaha _draw_pushup_overlays k liye method bna diye hai
    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

 # yaha _draw_curl_overlays k liye method bna diye hai
    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"SWING: {metrics['swing_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_lunge_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BALANCE: {metrics['balance_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

# yaha recv method me frame ko input lekr np array me convert kr denge

    def recv(self, frame):
        image = np.asarray(
            cv2.flip(frame.to_ndarray(format="bgr24"), 1), # hm same khade rah to ulta dihkta hai isliye fli used krte hai
            dtype=np.uint8 # data type ndarray me convert kr diye hai
        )

# agar hme Mediapipe k model ko used krni hai to uske formate me hi krna hoga
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, #yaha SRGB  hi used kr rahe hai MediaPipe k formate hai
            data=cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # yaha image ko pass krk data le rahe hai
        )

        self._frame_timestamps_ms += 30

        # yaha mp_img ko pass krk video detect kr rahe hai.yah image nad time stamp pass krne padte hai
        result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)

# yaha hme result aa chuka hai-->landmark me
        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

# ab hme landmark ko print bhi krne hai

            self._draw_skeleton(image, landmarks)

            ex_type = self.get_exercise()

            detector = self._detectors.get(ex_type)

            if detector:
                metrics = detector.process(landmarks)

                metrics["pose_detected"] = True

                self._draw_overlays(image, metrics, ex_type)

                self.set_latest_metrics(metrics)
        else:
            self._draw_no_pose_warnings(image)
            
            with self._lock:
                if self._latest_metrics is not None:
                    self._latest_metrics["pose_detected"] = False
                else:
                    self._latest_metrics = {"pose_detected": False}

# yaha av.VideoFrame me hi return krta hai recv() method

        return av.VideoFrame.from_ndarray(image, format="bgr24")
    