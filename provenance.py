import sqlite3
import hashlib

def store_image_hash(image_path):
    conn = sqlite3.connect("provenance.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS image_hashes (hash TEXT PRIMARY KEY, source TEXT)")
    
    with open(image_path, "rb") as img_file:
        img_hash = hashlib.sha256(img_file.read()).hexdigest()
    
    cursor.execute("INSERT OR IGNORE INTO image_hashes VALUES (?, ?)", (img_hash, image_path))
    conn.commit()
    conn.close()
    print("Image hash stored successfully.")

def verify_image_origin(image_path):
    conn = sqlite3.connect("provenance.db")
    cursor = conn.cursor()
    
    with open(image_path, "rb") as img_file:
        img_hash = hashlib.sha256(img_file.read()).hexdigest()
    
    cursor.execute("SELECT source FROM image_hashes WHERE hash=?", (img_hash,))
    result = cursor.fetchone()
    
    if result:
        print(f"Image origin verified! Source: {result[0]}")
    else:
        print("Image origin not found in the database.")
    
    conn.close()

if __name__ == "__main__":
    image_path = "data/tracked_data/output_steg.jpg"
    store_image_hash(image_path)
    verify_image_origin(image_path)
