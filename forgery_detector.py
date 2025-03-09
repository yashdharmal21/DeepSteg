import cv2
import numpy as np

def detect_image_tampering(image_path):
    img = cv2.imread(image_path, 0)
    edges = cv2.Canny(img, 100, 200)
    
    if np.mean(edges) > 50:
        print("Potential tampering detected!")
    else:
        print("No tampering detected.")

if __name__ == "__main__":
    image_path = "data/tracked_data/output_steg.jpg"
    detect_image_tampering(image_path)
