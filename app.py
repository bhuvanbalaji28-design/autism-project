from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import cv2
import mediapipe as mp
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ FIXED MEDIAPIPE (for Python 3.14)
mp_pose = mp.python.solutions.pose


# -------- LOAD MODEL --------
model = pickle.load(open("model.pkl", "rb"))


# -------- FEATURE EXTRACTION --------
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

            if prev is not None:
                movements.append(abs(lm.x - prev))

            prev = lm.x

    cap.release()

    return np.mean(movements) if movements else 0


# -------- AI CLASSIFICATION --------
def classify(video_path):
    feature = extract_features(video_path)

    prediction = model.predict([[feature]])[0]

    if prediction == 1:
        return "Autism Behavior Detected"
    else:
        return "Normal Behavior"


# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user == "admin" and pwd == "1234":
            session["user"] = user
            return redirect(url_for("home"))
        else:
            return "Invalid login"

    return render_template("login.html")


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# -------- HOME --------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    result = ""
    uploaded_video = ""

    if request.method == "POST":
        if "video" not in request.files:
            return "No file uploaded"

        file = request.files["video"]

        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        result = classify(filepath)
        uploaded_video = file.filename

    return render_template(
        "index.html",
        result=result,
        uploaded_video=uploaded_video
    )


# -------- SERVE VIDEO --------
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# -------- RUN (LOCAL ONLY) --------
if __name__ == "__main__":
    app.run()