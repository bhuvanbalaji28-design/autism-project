import streamlit as st
import os
import cv2
import mediapipe as mp
import numpy as np
import pickle

st.title("🧠 TinySignals AI")

# -------- LOAD MODEL --------
model = None
try:
    model = pickle.load(open("model.pkl", "rb"))
except:
    st.warning("Model not loaded, using basic prediction")

mp_pose = mp.solutions.pose


# -------- FEATURE EXTRACTION --------
def extract_features(video_path):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()

    movements = []
    prev = None
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count > 30:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            lm = result.pose_landmarks.landmark[0]

            if prev is not None:
                movements.append(abs(lm.x - prev))

            prev = lm.x

    cap.release()
    return np.mean(movements) if movements else 0


# -------- CLASSIFY --------
def classify(video_path):
    feature = extract_features(video_path)

    if model:
        pred = model.predict([[feature]])[0]
    else:
        pred = 0

    if pred == 1:
        return "Autism Behavior Detected", "autism"
    else:
        return "Normal Behavior", "normal"


# -------- DATASET VIDEO --------
def get_comparison(label):
    for file in os.listdir("dataset"):
        name = file.lower()
        if label == "autism" and ("arm" in name or "spin" in name or "head" in name):
            return os.path.join("dataset", file)
        if label == "normal" and "normal" in name:
            return os.path.join("dataset", file)
    return None


# -------- UI --------
uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:
    path = os.path.join("uploads", uploaded_file.name)

    with open(path, "wb") as f:
        f.write(uploaded_file.read())

    st.video(path)

    if st.button("Analyze"):
        result, label = classify(path)
        st.success(result)

        comp = get_comparison(label)

        if comp:
            st.write("### Comparison Video")
            st.video(comp)