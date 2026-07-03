import zipfile
import os

zip_path = r"C:\Summer intern '26 @Akashwani Bhawan\archive.zip"
extract_path = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\data\archive_dataset"

if not os.path.exists(zip_path):
    print(f"Error: {zip_path} does not exist.")
    exit(1)

os.makedirs(extract_path, exist_ok=True)

try:
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_path)
    print(f"Extracted to {extract_path}")
except Exception as e:
    print(f"Error extracting zip: {e}")
