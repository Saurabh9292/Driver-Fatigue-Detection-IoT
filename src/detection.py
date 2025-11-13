import cv2
import numpy as np
import dlib
import RPi.GPIO as GPIO
from imutils import face_utils
import time
import sys

# Redirect all output to log file
sys.stdout = open('/home/abcd@1234/fatigue-detection/fatigue_log.txt', 'a')
sys.stderr = sys.stdout

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUZZER_PIN = 18
RELAY_PIN = 26
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, False)
GPIO.output(RELAY_PIN, False)
print("GPIO initialized at", time.ctime())

# Thresholds
EAR_THRESHOLD = 0.25
MAR_THRESHOLD = 0.5
EAR_CONSEC_FRAMES = 48  # ~3 sec at 16 fps
MAR_CONSEC_FRAMES = 24  # ~1.5 sec at 16 fps

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Facial landmark indices
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# EAR and MAR calculation functions
def compute_ear(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

def compute_mar(mouth):
    A = np.linalg.norm(mouth[2] - mouth[10])
    B = np.linalg.norm(mouth[4] - mouth[8])
    C = np.linalg.norm(mouth[0] - mouth[6])
    return (A + B) / (2.0 * C)

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera at", time.ctime())
    GPIO.cleanup()
    exit()
print("Camera opened successfully at", time.ctime())

# Initialize counters and flags
ear_counter = 0
mar_counter = 0
alert_triggered = False
sprinkler_triggered = False
buzzer_start_time = None

# --------------------- MAIN LOOP ---------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera frame capture failed at", time.ctime())
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        left_eye = shape[lStart:lEnd]
        right_eye = shape[rStart:rEnd]
        mouth = shape[mStart:mEnd]

        ear = (compute_ear(left_eye) + compute_ear(right_eye)) / 2.0
        mar = compute_mar(mouth)

        # Log EAR and MAR
        print(f"EAR: {ear:.2f}, MAR: {mar:.2f} at {time.ctime()}")

        # Update counters
        ear_counter = ear_counter + 1 if ear < EAR_THRESHOLD else 0
        mar_counter = mar_counter + 1 if mar > MAR_THRESHOLD else 0

        current_time = time.time()

        # Trigger alert
        if (ear_counter >= EAR_CONSEC_FRAMES or mar_counter >= MAR_CONSEC_FRAMES) and not alert_triggered:
            alert_triggered = True
            buzzer_start_time = current_time
            GPIO.output(BUZZER_PIN, True)
            print("Fatigue Detected! Buzzer ON at", buzzer_start_time)

        elif alert_triggered:
            if (ear_counter >= EAR_CONSEC_FRAMES or mar_counter >= MAR_CONSEC_FRAMES):
                if current_time - buzzer_start_time > 5 and not sprinkler_triggered:
                    sprinkler_triggered = True
                    GPIO.output(RELAY_PIN, True)
                    print("Sprinkler ON at", current_time)
            else:
                if buzzer_start_time and current_time - buzzer_start_time <= 5:
                    alert_triggered = False
                    sprinkler_triggered = False
                    GPIO.output(BUZZER_PIN, False)
                    GPIO.output(RELAY_PIN, False)
                    print("Fatigue resolved in 5 seconds. Alert cleared at", time.ctime())
                elif buzzer_start_time and current_time - buzzer_start_time > 5 and sprinkler_triggered:
                    if ear_counter < EAR_CONSEC_FRAMES and mar_counter < MAR_CONSEC_FRAMES:
                        alert_triggered = False
                        sprinkler_triggered = False
                        GPIO.output(BUZZER_PIN, False)
                        GPIO.output(RELAY_PIN, False)
                        print("Fatigue resolved after sprinkler. All alerts OFF at", time.ctime())

    # --- Display code (commented for headless mode) ---
    # cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
    # cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)
    # cv2.drawContours(frame, [cv2.convexHull(mouth)], -1, (0, 255, 255), 1)
    # cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    # cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# Cleanup
cap.release()
GPIO.cleanup()
