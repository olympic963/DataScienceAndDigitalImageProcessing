import cv2
import numpy as np
import mediapipe as mp
import joblib
import paho.mqtt.client as mqtt
import ssl
# Load mô hình SVM và scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Hàm trích xuất landmarks
def extract_landmarks(hand_landmarks):
    landmarks = []
    for landmark in hand_landmarks.landmark:
        landmarks.extend([landmark.x, landmark.y, landmark.z])
    return landmarks

# Kết nối với MQTT broker
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("olympic963", "Anacondaxs5")  # Cân nhắc bảo mật thông tin này
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)  # Kích hoạt TLS
mqtt_client.connect("c57cbf5b18cf41adb470c9a868a7c9a4.s1.eu.hivemq.cloud", 8883, 60)
mqtt_client.loop_start()
# Các biến để theo dõi trạng thái
last_gesture = None
# Khởi tạo camera
# url = 'http://192.168.1.184:81/stream'
# cap = cv2.VideoCapture(url)
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            label = 'Right Hand' if handedness.classification[0].label == 'Right' else 'Left Hand'
            landmarks = extract_landmarks(hand_landmarks)
            landmarks = scaler.transform([landmarks])
            gesture = model.predict(landmarks)[0]
            if gesture == 0:
                gesture_text = 'Nam Tay'
            elif gesture == 1:
                gesture_text = 'Bat Den 1'
            elif gesture == 2:
                gesture_text = 'Bat Den 2'
            elif gesture == 3:
                gesture_text = 'Bat Den 3'
            elif gesture == 4:
                gesture_text = 'Xoe Tay'
            else:
                gesture_text = 'Unknown'
            text_location = (50, 50) if label == 'Left Hand' else (frame.shape[1] - 200, 50)
            cv2.putText(frame, label, text_location, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            gesture_location = (text_location[0], text_location[1] + 30)
            cv2.putText(frame, gesture_text, gesture_location, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # Kiểm tra sự thay đổi cử chỉ và chỉ xử lý khi có một tay
            if len(results.multi_hand_landmarks) == 1 and gesture != last_gesture:
                last_gesture = gesture
                if gesture == 0:  # Nam Tay
                    mqtt_client.publish("ESP32/deviceControl", "off1")
                    mqtt_client.publish("ESP32/deviceControl", "off2")
                    mqtt_client.publish("ESP32/deviceControl", "off3")
                elif gesture == 1:  # Bat Den 1
                    mqtt_client.publish("ESP32/deviceControl", "on1")
                elif gesture == 2:  # Bat Den 2
                    mqtt_client.publish("ESP32/deviceControl", "on2")
                elif gesture == 3:  # Bat Den 3
                    mqtt_client.publish("ESP32/deviceControl", "on3")
                elif gesture == 4:  # Xoe Tay
                    mqtt_client.publish("ESP32/deviceControl", "on1")
                    mqtt_client.publish("ESP32/deviceControl", "on2")
                    mqtt_client.publish("ESP32/deviceControl", "on3")
    cv2.imshow('Hand Gesture Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
