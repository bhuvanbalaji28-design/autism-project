from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- SIMPLE AI --------
def classify(filename):
    name = filename.lower()

    if "arm" in name:
        return "Autism Behavior Detected (Arm Movement)", "autism"
    elif "spin" in name:
        return "Autism Behavior Detected (Spinning)", "autism"
    elif "head" in name:
        return "Autism Behavior Detected (Head Movement)", "autism"
    else:
        return "Normal Behavior", "normal"


# -------- DATASET VIDEO --------
def get_comparison_video(label):
    for file in os.listdir(DATASET_FOLDER):
        name = file.lower()

        if label == "autism":
            if "arm" in name or "spin" in name or "head" in name:
                return file
        else:
            if "normal" in name:
                return file

    return ""


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


# -------- HOME --------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    result = ""
    uploaded_video = ""
    comparison_video = ""

    if request.method == "POST":
        file = request.files["video"]

        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        result, label = classify(file.filename)
        uploaded_video = file.filename

        comparison_video = get_comparison_video(label)

    return render_template(
        "index.html",
        result=result,
        uploaded_video=uploaded_video,
        comparison_video=comparison_video
    )


# -------- SERVE FILES --------
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/dataset/<filename>')
def dataset_file(filename):
    return send_from_directory(DATASET_FOLDER, filename)


if __name__ == "__main__":
    app.run()