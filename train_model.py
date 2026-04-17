import os
import cv2
import mediapipe as mp
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

DATASET = "dataset"

mp_pose = mp.solutions.pose


def extract_features(video_path):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()

    movements = []

    prev = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            lm = result.pose_landmarks.landmark[0]  # nose

            if prev:
                movements.append(abs(lm.x - prev))

            prev = lm.x

    cap.release()

    return np.mean(movements) if movements else 0


X = []
y = []

print("Training started...")

for file in os.listdir(DATASET):
    path = os.path.join(DATASET, file)

    feature = extract_features(path)

    if "arm" in file.lower() or "head" in file.lower() or "spin" in file.lower():
        label = 1   # autism
    else:
        label = 0   # normal

    X.append([feature])
    y.append(label)

model = RandomForestClassifier()
model.fit(X, y)

# save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved ✅")