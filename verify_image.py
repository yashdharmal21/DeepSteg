import cv2
import hashlib
import mysql.connector
import numpy as np
from deepface import DeepFace
from PIL import Image, ImageChops

# Database Connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yash",
        database="deepsteg_db"
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(f"❌ Database Connection Error: {err}")
    exit()

# Image Path (Test with modified image)
image_path = "C:/Users/yashd/OneDrive/Desktop/DeepSteg/data/test_images/IMG_5055.jpg"

# Compute SHA-256 Hash
def compute_hash(image_path):
    with open(image_path, "rb") as f:
        img_data = f.read()
    return hashlib.sha256(img_data).hexdigest()

# Check if Hash Exists in DB
def check_hash_in_db(image_hash):
    cursor.execute("SELECT * FROM images WHERE image_hash = %s", (image_hash,))
    return cursor.fetchone()

# Register Hash in DB
def register_hash_in_db(image_hash):
    cursor.execute("INSERT INTO images (image_hash) VALUES (%s)", (image_hash,))
    conn.commit()

# Error Level Analysis (ELA) for Forgery Detection
def error_level_analysis(image_path):
    image = Image.open(image_path).convert("RGB")
    resaved_path = "temp_resaved.jpg"
    image.save(resaved_path, quality=90)
    
    resaved = Image.open(resaved_path)
    ela_image = ImageChops.difference(image, resaved)
    
    extrema = ela_image.getextrema()
    max_diff = max([max(e) for e in extrema])
    
    if max_diff > 50:  # Threshold for significant manipulation
        return True, max_diff  # Image is likely manipulated
    return False, max_diff

# DeepFake Detection Using DeepFace
def detect_deepfake(image_path):
    try:
        DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        return False  # No deepfake detected
    except Exception as e:
        return True  # Likely manipulated or AI-generated image

# Compute Hash & Verify
computed_hash = compute_hash(image_path)
stored_hash = check_hash_in_db(computed_hash)

print(f"🔍 Computed Hash: {computed_hash}")

if stored_hash:
    print("✅ Image Verified! Hash Matched in DB.")
else:
    print("⚠️ WARNING: Image Hash NOT Found in DB!")
    register_hash_in_db(computed_hash)
    print(f"✅ New Image Registered! Hash Stored: {computed_hash}")

# Check for Edits (ELA)
ela_result, ela_diff = error_level_analysis(image_path)
if ela_result:
    print(f"⚠️ Possible Forgery Detected (ELA) - Manipulation Score: {ela_diff}")
else:
    print("✅ No major edits detected (ELA)")

# Check for DeepFake
deepfake_detected = detect_deepfake(image_path)
if deepfake_detected:
    print("⚠️ WARNING: Image may be DeepFake or AI-manipulated!")
else:
    print("✅ No DeepFake detected.")

# Close DB Connection
cursor.close()
conn.close()
