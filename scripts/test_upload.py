"""
Quick test: upload just 1 image to diagnose issues
"""

import json
from pathlib import Path
import cloudinary
import cloudinary.uploader
from decouple import config

ROOT = Path(__file__).parent.parent

print(f"ROOT: {ROOT}")
print(f"Config:")
print(f"  API_NAME: {config('API_NAME').strip()}")
print(f"  API_KEY: {config('API_KEY').strip()[:10]}...")
print(f"  API_SECRET: {config('API_SECRET').strip()[:10]}...")

cloudinary.config(
    cloud_name=config("API_NAME").strip(),
    api_key=config("API_KEY").strip(),
    api_secret=config("API_SECRET").strip(),
    secure=True,
)

# Test with just the logo
test_file = ROOT / "mw_web" / "img" / "mwecau.png"
print(f"\nTest file: {test_file}")
print(f"Exists: {test_file.exists()}")

if test_file.exists():
    try:
        print(f"\nUploading...")
        resp = cloudinary.uploader.upload(
            str(test_file),
            public_id="mwecau/logo/mwecau",
            overwrite=False,
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )
        print(f"✅ SUCCESS: {resp['secure_url']}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
