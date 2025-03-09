import cv2
import numpy as np
import stegano
from stegano.lsb import hide

def embed_tracking_data(image_path, tracking_data, output_path):
    try:
        # Hide tracking data in image using LSB steganography
        secret_img = hide(image_path, tracking_data)
        secret_img.save(output_path)
        print(f"Tracking data embedded successfully in {output_path}")
    except Exception as e:
        print(f"Error embedding tracking data: {e}")

if __name__ == "__main__":
    image_path = r"C:\Users\yashd\OneDrive\Desktop\DeepSteg\data\test_images\IMG_5053.jpg"
    tracking_data = "UniqueID:12345;Uploader:JohnDoe;Timestamp:2025-03-08"
    output_path = "data/tracked_data/output_steg.jpg"
    embed_tracking_data(image_path, tracking_data, output_path)
