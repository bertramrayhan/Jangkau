# File: sync_models.py

import shutil
import os

# File master untuk Flask
SOURCE_FILE = os.path.join('database', 'models_flask.py')

# File tujuan yang akan digunakan oleh webapp
DESTINATION_FILE = os.path.join('webapp', 'models.py')

print(f"Copying '{SOURCE_FILE}' to '{DESTINATION_FILE}'...")

try:
    shutil.copyfile(SOURCE_FILE, DESTINATION_FILE)
    print("✅ Sync complete.")
except FileNotFoundError:
    print(f"❌ ERROR: Source file not found at '{SOURCE_FILE}'.")
    # Keluar dengan error agar pre-commit gagal jika file master tidak ada
    exit(1) 
except Exception as e:
    print(f"❌ ERROR: An unexpected error occurred: {e}")
    exit(1)