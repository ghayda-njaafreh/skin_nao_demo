# -*- coding: utf-8 -*-
import sys
import time
import random

sys.path.insert(0, r'C:\Users\DELL\Downloads\pythonSDK\lib')

from naoqi import ALProxy

NAO_IP     = "172.25.160.183"   
NAO_PORT = 9559

DISPLAY_COLORS = {
    "green": 0x00FF00,
    "red":   0xFF0000,
    "white": 0xFFFFFF,
}

def get_eye_color(predicted_class_code):
    if predicted_class_code == "nv":
        return DISPLAY_COLORS["green"]
    return DISPLAY_COLORS["red"]

def prepare_robot(posture, motion):
    try:
        posture.goToPosture("StandInit", 0.6)
    except Exception as e:
        print("Posture warning:", e)

    try:
        motion.setStiffnesses("Arms", 1.0)
        motion.setStiffnesses("Head", 1.0)
    except Exception as e:
        print("Stiffness warning:", e)

def set_eye_color(leds, color_value):
    try:
        leds.fadeRGB("FaceLeds", color_value, 0.2)
    except Exception as e:
        print("LED warning:", e)

def reset_eye_color(leds):
    try:
        leds.fadeRGB("FaceLeds", DISPLAY_COLORS["white"], 0.3)
    except Exception as e:
        print("LED reset warning:", e)

def center_head(motion):
    try:
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.0, -0.05],
            [0.4, 0.4],
            True
        )
    except Exception as e:
        print("Head center warning:", e)

def reset_arms(motion):
    try:
        names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"
        ]
        angles = [
            1.50,  0.15, -1.20, -0.50,
            1.50, -0.15,  1.20,  0.50
        ]
        times = [0.8] * len(names)
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Arm reset warning:", e)

def gesture_benign_soft(motion):
    try:
        names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"
        ]
        angles = [
            1.25,  0.18, -0.95, -0.55,
            1.25, -0.18,  0.95,  0.55
        ]
        times = [0.8] * len(names)
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Benign gesture warning:", e)

def gesture_benign_followup(motion):
    try:
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.08, -0.08],
            [0.35, 0.35],
            True
        )
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.0, -0.05],
            [0.30, 0.30],
            True
        )
    except Exception as e:
        print("Benign follow-up warning:", e)

def gesture_intermediate_explain(motion):
    try:
        names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"
        ]
        angles = [
            1.18,  0.22, -0.90, -0.65,
            1.18, -0.22,  0.90,  0.65
        ]
        times = [0.75] * len(names)
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Intermediate gesture warning:", e)

def gesture_intermediate_followup(motion):
    try:
        names = ["LShoulderPitch", "RShoulderPitch"]
        angles = [1.30, 1.30]
        times = [0.45, 0.45]
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Intermediate follow-up warning:", e)

def gesture_alert_right_hand(motion):
    try:
        names = [
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"
        ]
        angles = [
            1.00, -0.32, 1.10, 0.70,
            1.40,  0.10, -1.15, -0.45
        ]
        times = [0.75] * len(names)
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Alert gesture 1 warning:", e)

def gesture_alert_left_hand(motion):
    try:
        names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"
        ]
        angles = [
            1.00, 0.32, -1.10, -0.70,
            1.40, -0.10, 1.15, 0.45
        ]
        times = [0.75] * len(names)
        motion.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Alert gesture 2 warning:", e)

def gesture_alert_followup(motion):
    try:
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.10, -0.10],
            [0.30, 0.30],
            True
        )
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [-0.08, -0.03],
            [0.30, 0.30],
            True
        )
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.0, -0.05],
            [0.25, 0.25],
            True
        )
    except Exception as e:
        print("Alert follow-up warning:", e)

def perform_contextual_gesture(motion, predicted_class_code):
    if predicted_class_code == "nv":
        gesture_benign_soft(motion)
        time.sleep(0.15)
        gesture_benign_followup(motion)
        return

    if predicted_class_code in {"mel", "bcc", "akiec"}:
        if int(time.time()) % 2 == 0:
            gesture_alert_right_hand(motion)
        else:
            gesture_alert_left_hand(motion)
        time.sleep(0.15)
        gesture_alert_followup(motion)
        return

    gesture_intermediate_explain(motion)
    time.sleep(0.15)
    gesture_intermediate_followup(motion)

def speak_text(text, predicted_class_code):
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)

    tts.setLanguage("English")
    tts.setParameter("speed", 88.0)

    print("NAO will say:", text)
    print("Predicted class code:", predicted_class_code)

    prepare_robot(posture, motion)
    center_head(motion)

    color_value = get_eye_color(predicted_class_code)
    set_eye_color(leds, color_value)

    perform_contextual_gesture(motion, predicted_class_code)

    tts.say(text)

    time.sleep(0.25)
    reset_arms(motion)
    center_head(motion)
    time.sleep(0.5)
    reset_eye_color(leds)

    print("Speech command executed.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nao_speaker.py \"text\" predicted_class_code")
        sys.exit(1)

    text = sys.argv[1]
    predicted_class_code = sys.argv[2]

    speak_text(text, predicted_class_code)
    print("Speech sent successfully.")
