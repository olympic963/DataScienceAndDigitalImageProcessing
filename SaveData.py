import cv2
import mediapipe as mp
import os
import mysql.connector
from mysql.connector import Error
def process_images(folder_path, table_name, cursor, connection):
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Không thể tải ảnh: {image_path}")
            continue
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        landmark_data = ["0;0;0"] * 21  # Mặc định nếu không có tay
        if not results.multi_hand_landmarks:
            print("Không phát hiện tay trong ảnh, đang xóa ảnh:", image_name)
            os.remove(image_path)
            continue  # Bỏ qua việc chèn dữ liệu và xóa ảnh nếu không phát hiện tay
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_data = [f"{round(landmark.x, 5)};{round(landmark.y, 5)};{round(landmark.z, 10)}" for landmark in hand_landmarks.landmark]
                if len(landmark_data) == 21:
                    break  # Chỉ xử lý tay đầu tiên được phát hiện
        sql = (
            f"INSERT INTO {table_name} (ten_file_anh, wrist, thumb_cmc, thumb_mcp, thumb_ip, thumb_tip, "
            "index_finger_mcp, index_finger_pip, index_finger_dip, index_finger_tip, middle_finger_mcp, "
            "middle_finger_pip, middle_finger_dip, middle_finger_tip, ring_finger_mcp, ring_finger_pip, "
            "ring_finger_dip, ring_finger_tip, pinky_mcp, pinky_pip, pinky_dip, pinky_tip) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(sql, (image_name, *landmark_data))
        connection.commit()
# Thiết lập MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

# Kết nối với cơ sở dữ liệu MySQL
try:
    connection = mysql.connector.connect(host='localhost', database='iotweb', user='root', password='olympic963')
    if connection.is_connected():
        cursor = connection.cursor()
        # folders = {
        #     r'D:\Xulyanh\Namtay\train': 'namtay_train',
        #     r'D:\Xulyanh\Namtay\test': 'namtay_test',
        #     r'D:\Xulyanh\Xoetay\train': 'xoetay_train',
        #     r'D:\Xulyanh\Xoetay\test': 'xoetay_test',
        #     r'D:\Xulyanh\Batden1\train': 'batden1_train',
        #     r'D:\Xulyanh\Batden1\test': 'batden1_test',
        #     r'D:\Xulyanh\Batden2\train': 'batden2_train',
        #     r'D:\Xulyanh\Batden2\test': 'batden2_test',
        #     r'D:\Xulyanh\Batden3\train': 'batden3_train',
        #     r'D:\Xulyanh\Batden3\test': 'batden3_test'
        # }
        folders = {
            r'D:\btl\Namtay': 'namtay',
            r'D:\btl\Xoetay': 'xoetay',
            r'D:\btl\Batden1': 'batden1',
            r'D:\btl\Batden2': 'batden2',
            r'D:\btl\Batden3': 'batden3'
        }
        for folder_path, table_name in folders.items():
            process_images(folder_path, table_name, cursor, connection)
        print("All images have been processed and data inserted into the database.")
except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
