import zipfile
import os

zip_path = r"C:\Summer intern '26 @Akashwani Bhawan\archive.zip"

if not os.path.exists(zip_path):
    print(f"Error: {zip_path} does not exist.")
    exit(1)

try:
    with zipfile.ZipFile(zip_path) as z:
        print("Files in archive.zip:")
        for name in z.namelist():
            print(name)
except Exception as e:
    print(f"Error reading zip: {e}")
