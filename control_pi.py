import cv2
import mediapipe as mp
import RPi.GPIO as GPIO
import time

# LED GPIO Pins (Adjust as needed)
LED_PINS = [17, 18, 27, 22, 23]  # GPIO17, GPIO18, GPIO27, GPIO22, GPIO23

# Raspberry Pi GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PINS, GPIO.OUT)

class HandTracker:
    def __init__(self, maxHands=2, detectionCon=0.7, trackCon=0.7):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=maxHands,
                                        min_detection_confidence=detectionCon,
                                        min_tracking_confidence=trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]  # Thumb & Fingers

    def findHands(self, frame, draw=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks and draw:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)
        return frame

    def findPosition(self, frame):
        lmsList = []
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmsList.append([id, cx, cy])
        return lmsList

    def fingersUp(self):
        fingers = []
        if self.lmsList[self.tipIds[0]][1] > self.lmsList[self.tipIds[0] - 1][1]:  # Thumb
            fingers.append(1)
        else:
            fingers.append(0)

        for i in range(1, 5):  # Other fingers
            if self.lmsList[self.tipIds[i]][2] < self.lmsList[self.tipIds[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

def control_leds(finger_count):
    # Turn off all LEDs first
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.LOW)

    # Light up LEDs based on finger count
    for i in range(finger_count):
        GPIO.output(LED_PINS[i], GPIO.HIGH)

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = tracker.findHands(frame)
        tracker.lmsList = tracker.findPosition(frame)

        if tracker.lmsList:
            fingers = tracker.fingersUp()
            count = fingers.count(1)
            cv2.putText(frame, f"Fingers: {count}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            control_leds(count)  # Control LEDs based on finger count

        cv2.imshow("Hand Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
