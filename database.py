import mysql.connector
import hashlib

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yash",
    "database": "deepsteg_db"
}

def get_image_hash(image_path):
    """Generate SHA-256 hash of the given image."""
    sha256 = hashlib.sha256()
    with open(image_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def check_hash_exists(image_hash):
    """Check if the hash already exists in the database."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM images WHERE image_hash = %s", (image_hash,))
    exists = cursor.fetchone()  # Fetch one result

    cursor.close()
    conn.close()
    
    return exists is not None  # True if hash exists, False otherwise

def store_image_hash(image_path):
    """Store image hash in MySQL only if it does not exist."""
    image_hash = get_image_hash(image_path)

    if check_hash_exists(image_hash):
        print("⚠️ Image is already stored in the database!")
        return False  # Duplicate found, do not store

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO images (image_hash) VALUES (%s)", (image_hash,))
        conn.commit()

        print(f"✅ Your image has generated a unique hashcode: {image_hash}")

        cursor.close()
        conn.close()
        return True  # Successfully stored

    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return False
