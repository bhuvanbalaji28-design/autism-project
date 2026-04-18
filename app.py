from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- SIMPLE AI (SAFE VERSION) --------
def classify(filename):
    name = filename.lower()

    if "arm" in name:
        return "Autism Behavior Detected (Arm Movement)"
    elif "spin" in name:
        return "Autism Behavior Detected (Spinning)"
    elif "head" in name:
        return "Autism Behavior Detected (Head Movement)"
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
        file = request.files["video"]

        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        result = classify(file.filename)
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


# -------- RUN --------
if __name__ == "__main__":
    app.run()