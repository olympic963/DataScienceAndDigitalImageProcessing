import cv2
import mediapipe as mp
import os
import time

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Đường dẫn thư mục để lưu ảnh
save_path = 'D:/btl/Batden3'  # Thay thế với đường dẫn thực tế của bạn
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Khởi tạo camera
# url = 'http://192.168.1.184:81/stream'
# cap = cv2.VideoCapture(url)
cap = cv2.VideoCapture(0)
# Cờ để theo dõi việc lưu ảnh
image_saved = False
save_message = ""

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Không thể nhận hình ảnh từ camera, kiểm tra lại thiết bị.")
        break
    frame = cv2.flip(frame, 1)
    # Nếu ảnh đã được lưu, hiển thị thông báo
    if image_saved:
        cv2.putText(frame, save_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        image_saved = False  # Reset lại cờ sau khi hiển thị thông báo

    # Chuyển đổi màu từ BGR sang RGB để MediaPipe có thể xử lý
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Nhận diện chỉ tay
    results = hands.process(rgb_frame)
    frame_to_save = frame.copy()
    # Vẽ chỉ tay lên hình ảnh (chỉ để hiển thị)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Hiển thị hình ảnh
    cv2.imshow('Camera Output', frame)

    # Nhấn 'q' để thoát, 's' để lưu ảnh
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Lưu ảnh không có chỉ tay vào thư mục đã chọn
        img_name = os.path.join(save_path, 'image_{}.png'.format(time.strftime("%Y%m%d_%H%M%S")))
        cv2.imwrite(img_name,frame_to_save )
        save_message = "Da luu"
        image_saved = True
        print(save_message)

# Giải phóng tài nguyên và đóng tất cả cửa sổ
cap.release()
cv2.destroyAllWindows()
hands.close()
