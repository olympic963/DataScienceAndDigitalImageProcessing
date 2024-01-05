import mysql.connector
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
# Hàm để lấy dữ liệu từ cơ sở dữ liệu
def fetch_data(cursor, table_name):
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    data = []
    for row in rows:
        landmarks = []
        for i in range(2, 23):  # Lấy 21 cột chứa landmarks
            x, y, z = map(float, row[i].split(';'))
            landmarks.extend([x, y, z])
        data.append(landmarks)
    return data

# Kết nối với cơ sở dữ liệu
conn = mysql.connector.connect(
    host='localhost',
    database='iotweb',
    user='root',
    password='olympic963'
)
cursor = conn.cursor()
# Truy xuất dữ liệu từ mỗi bảng
namtay_data = fetch_data(cursor, 'namtay')
xoetay_data = fetch_data(cursor, 'xoetay')
batden1_data = fetch_data(cursor, 'batden1')
batden2_data = fetch_data(cursor, 'batden2')
batden3_data = fetch_data(cursor, 'batden3')

# Gán nhãn
namtay_labels = [0] * len(namtay_data)
batden1_labels = [1] * len(batden1_data)
batden2_labels = [2] * len(batden2_data)
batden3_labels = [3] * len(batden3_data)
xoetay_labels = [4] * len(xoetay_data)

# Gộp dữ liệu và nhãn
X = namtay_data + xoetay_data + batden1_data + batden2_data + batden3_data
y = namtay_labels + xoetay_labels + batden1_labels + batden2_labels + batden3_labels
# Chia tập dữ liệu thành train và test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#Huấn luyện mô hình SVM
model = SVC(kernel='linear')
model.fit(X_train_scaled, y_train)
# model = RandomForestClassifier(n_estimators=5, random_state=42)  # Sử dụng RandomForestClassifier
# model.fit(X_train_scaled, y_train)
# model = GradientBoostingClassifier(random_state=42)
# model.fit(X_train_scaled, y_train)
# model = XGBClassifier(random_state=42)
# model.fit(X_train_scaled, y_train)
# model = KNeighborsClassifier(n_neighbors=5)
# model.fit(X_train_scaled, y_train)

# Dự đoán trên tập dữ liệu kiểm tra
y_pred = model.predict(X_test_scaled)

cm = confusion_matrix(y_test, y_pred)
print(f"Confusion Matrix:\n{cm}")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='macro')
recall = recall_score(y_test, y_pred, average='macro')
f1 = f1_score(y_test, y_pred, average='macro')
print(f"Accuracy (Độ chính xác tổng thể): {accuracy:.2f}")
print(f"Precision (Độ chính xác của dự đoán tích cực): {precision:.2f}")
print(f"Recall (Độ nhạy, tỷ lệ phát hiện chính xác các trường hợp tích cực): {recall:.2f}")
print(f"F1 Score (Điểm F1, trung bình điều hòa giữa Precision và Recall): {f1:.2f}")


# Lưu mô hình và scaler
dump(model, 'model.pkl')
dump(scaler, 'scaler.pkl')

# Đóng kết nối cơ sở dữ liệu
cursor.close()
conn.close()