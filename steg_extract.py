import stegano
from stegano.lsb import reveal

def extract_tracking_data(image_path):
    try:
        extracted_data = reveal(image_path)
        print(f"Extracted Tracking Data: {extracted_data}")
        return extracted_data
    except Exception as e:
        print(f"Error extracting tracking data: {e}")

if __name__ == "__main__":
    image_path = "data/tracked_data/output_steg.jpg"
    extract_tracking_data(image_path)
