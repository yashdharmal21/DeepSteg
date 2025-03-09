from steg_embed import embed_tracking_data
from steg_extract import extract_tracking_data
from deepfake_detector import detect_deepfake
from provenance import store_image_hash, verify_image_origin
from forgery_detector import detect_image_tampering

image_path = r"C:\Users\yashd\OneDrive\Desktop\DeepSteg\data\test_images\IMG_5053.jpg"
output_path = "data/tracked_data/output_steg.jpg"
tracking_data = "UniqueID:67890;Uploader:Yash;Timestamp:2025-03-08"

embed_tracking_data(image_path, tracking_data, output_path)
extract_tracking_data(output_path)
detect_deepfake(output_path)
store_image_hash(output_path)
verify_image_origin(output_path)
detect_image_tampering(output_path)
