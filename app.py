from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import cv2
import mediapipe as mp

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mp_pose = mp.solutions.pose


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


# -------- MEDIAPIPE FEATURE --------
def extract_features(video_path):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()

    movements = 0
    frames = 0

    while True:
        ret, frame = cap.read()
        if not ret or frames > 50:
            break

        frames += 1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            movements += 1

    cap.release()
    return movements


# -------- CLASSIFICATION --------
def classify(video_path):
    movement = extract_features(video_path)

    if movement > 20:
        return "Autism Behavior Detected"
    else:
        return "Normal Behavior"


# -------- HOME --------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    result = ""
    uploaded_video = ""

    if request.method == "POST":
        file = request.files["video"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        result = classify(path)
        uploaded_video = file.filename

    return render_template("index.html",
        result=result,
        uploaded_video=uploaded_video
    )


# -------- SERVE VIDEO --------
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# -------- RUN --------
if __name__ == "__main__":
    app.run()