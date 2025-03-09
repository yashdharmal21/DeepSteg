from deepface import DeepFace

def detect_deepfake(image_path):
    try:
        result = DeepFace.analyze(image_path, actions=['age', 'gender', 'emotion'])
        print(f"Deepfake Detection Result: {result}")
    except Exception as e:
        print(f"Error detecting deepfake: {e}")

if __name__ == "__main__":
    image_path = "data/tracked_data/output_steg.jpg"
    detect_deepfake(image_path)
