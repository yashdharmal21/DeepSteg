from flask import Flask, render_template, request, jsonify
import os
from verify_image import compute_hash, error_level_analysis, detect_deepfake
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash",
    database="deepsteg_db"
)
cursor = conn.cursor()

def check_hash_in_db(image_hash):
    cursor.execute("SELECT * FROM images WHERE image_hash = %s", (image_hash,))
    return cursor.fetchone()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'image' not in request.files:
        return jsonify({"message": "No file uploaded!"}), 400

    image = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    image_hash = compute_hash(image_path)
    hash_exists = check_hash_in_db(image_hash)

    ela_result, ela_diff = error_level_analysis(image_path)
    deepfake_detected = detect_deepfake(image_path)

    response = {
        "hash": image_hash,
        "exists_in_db": bool(hash_exists),
        "ela_detected": ela_result,
        "ela_score": ela_diff,
        "deepfake_detected": deepfake_detected,
        "message": "✅ Image Verified!" if hash_exists else "⚠️ WARNING: Image NOT found in DB!"
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

