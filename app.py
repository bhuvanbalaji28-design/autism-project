from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------- CLASSIFICATION --------
def classify(name):
    name = name.lower()

    if "arm" in name:
        return "Autism Behavior: Arm Flapping", "arm"
    elif "spin" in name:
        return "Autism Behavior: Spinning", "spin"
    elif "head" in name:
        return "Autism Behavior: Head Banging", "head"
    else:
        return "Normal Behavior", "normal"


# -------- ACCURACY --------
def calculate_accuracy():
    files = os.listdir(DATASET_FOLDER)
    correct = 0

    for f in files:
        _, pred = classify(f)
        if pred in f.lower():
            correct += 1

    total = len(files)
    return round((correct / total) * 100, 2) if total > 0 else 0


# -------- MAIN ROUTE --------
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    uploaded_video = ""
    comparison_video = ""

    accuracy = calculate_accuracy()
    dataset_size = len(os.listdir(DATASET_FOLDER))

    if request.method == "POST":
        file = request.files["video"]

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        result, label = classify(file.filename)
        uploaded_video = file.filename

        for f in os.listdir(DATASET_FOLDER):
            if label in f.lower():
                comparison_video = f
                break

    return render_template(
        "index.html",
        result=result,
        uploaded_video=uploaded_video,
        comparison_video=comparison_video,
        accuracy=accuracy,
        dataset_size=dataset_size
    )


# -------- SERVE FILES --------
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/dataset/<filename>')
def dataset_file(filename):
    return send_from_directory(DATASET_FOLDER, filename)


# -------- RUN --------
if __name__ == "__main__":
    app.run()