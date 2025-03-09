import hashlib

def get_image_hash(image_path):
    with open(image_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

original = get_image_hash("C:\\Users\\yashd\\OneDrive\\Desktop\\DeepSteg\\data\\test_images\\IMG_5054.jpg")
modified = get_image_hash("C:\\Users\\yashd\\OneDrive\\Desktop\\DeepSteg\\data\\test_images\\IMG_5064.jpg")

print(f"Original Hash: {original}")
print(f"Modified Hash: {modified}")
print("Hashes match!" if original == modified else "Hashes DO NOT match!")
