from flask import Flask, request, jsonify, render_template
import hashlib
import mysql.connector
import os
from PIL import Image
import imagehash
import piexif
import zipfile

app = Flask(__name__, static_folder="static", template_folder="templates")

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yash",
    "database": "deepsteg_db"
}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def compute_sha256(image_path):
    try:
        with open(image_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"⚠️ Error computing SHA-256: {e}")
        return None

def compute_phash(image_path):
    try:
        img = Image.open(image_path)
        return str(imagehash.phash(img))
    except Exception as e:
        print(f"⚠️ Error computing pHash: {e}")
        return None

def embed_exif_hash(image_path, image_hash):
    try:
        img = Image.open(image_path)

        if img.format != "JPEG":
            print(f"⚠️ Skipping EXIF embedding: {img.format} does not support EXIF metadata.")
            return

        # Load existing EXIF data or create new
        exif_dict = piexif.load(img.info["exif"]) if "exif" in img.info else {"Exif": {}}

        # Embed the hash in EXIF UserComment
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = image_hash.encode("utf-8")
        exif_bytes = piexif.dump(exif_dict)

        # Save with new EXIF data
        img.save(image_path, "jpeg", exif=exif_bytes)
        print("✅ Hash successfully embedded in EXIF metadata")

    except KeyError:
        print("⚠️ No existing EXIF metadata found, skipping embedding.")
    except Exception as e:
        print(f"⚠️ Error embedding EXIF metadata: {e}")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"message": "⚠️ No file uploaded!"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"message": "⚠️ No file selected!"}), 400

    temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_path)  # Save temporarily before zipping

    # Compute hashes
    image_sha256 = compute_sha256(temp_path)
    image_phash = compute_phash(temp_path)

    if image_sha256 is None or image_phash is None:
        return jsonify({"message": "⚠️ Error computing image hashes!"}), 500

    # Check if hash already exists in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE image_sha256 = %s", (image_sha256,))
    existing_image = cursor.fetchone()

    if existing_image:
        cursor.close()
        conn.close()
        os.remove(temp_path)  # ✅ Remove temp file if already in DB
        return jsonify({"message": "✅ Image already exists in the database, So the image is Authentic!"}), 200  

    # Embed hash in EXIF metadata (if applicable)
    embed_exif_hash(temp_path, image_sha256)

    # Store image in ZIP
    zip_path = os.path.join(UPLOAD_FOLDER, "uploads.zip")
    with zipfile.ZipFile(zip_path, "a") as zipf:
        zipf.write(temp_path, arcname=file.filename)  # Add image to ZIP

    os.remove(temp_path)  # ✅ Delete the original image to save space

    # Store hash in database
    cursor.execute(
        "INSERT INTO images (image_hash, image_sha256, image_phash) VALUES (%s, %s, %s)",
        (image_sha256, image_sha256, image_phash)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"⚠️ Image stored in ZIP with hash, So the may file be Tampered: {image_sha256}"})

@app.route("/check_integrity", methods=["POST"])
def check_image_integrity():
    if "image" not in request.files:
        return jsonify({"message": "⚠️ No file uploaded!"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"message": "⚠️ No file selected!"}), 400

    temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_path)

    image_sha256 = compute_sha256(temp_path)
    image_phash = compute_phash(temp_path)

    if not image_sha256 or not image_phash:
        return jsonify({"message": "⚠️ Error computing image hashes!"}), 500

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_sha256, image_phash FROM images")
    existing_hashes = cursor.fetchall()

    for stored_sha256, stored_phash in existing_hashes:
        if stored_sha256 == image_sha256:
            return jsonify({"message": "✅ Image is authentic (Exact Match)"})

        if stored_phash:
            hamming_distance = imagehash.hex_to_hash(stored_phash) - imagehash.hex_to_hash(image_phash)
            if hamming_distance == 0:
                return jsonify({"message": "✅ Image is authentic (Perceptual Match)"})
            elif hamming_distance < 5:
                return jsonify({"message": "⚠️ Possible tampering detected!"})
    
    cursor.close()
    conn.close()
    return jsonify({"message": "❌ Image not found in database! Possible manipulation detected."})

if __name__ == "__main__":
    app.run(debug=True)