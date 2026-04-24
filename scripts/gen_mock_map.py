"""
Generate mock Cloudinary URL mapping for testing path replacement logic.
Simulates what the upload would produce. Run real upload later when you have time.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Collect all images and generate mock URLs
EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".JPG", ".JPEG", ".PNG"}

def get_folder(path: Path) -> str:
    rel = path.relative_to(ROOT / "mw_web")
    parts = rel.parts

    if parts[0] == "img":
        if path.stem.lower() == "mwecau" and path.suffix == ".png":
            return "mwecau/logo"
        if len(parts) >= 2 and parts[1] == "campus-life":
            return "mwecau/campus"
        return "mwecau/banners"

    if parts[0] == "images":
        sub = parts[1].lower() if len(parts) > 1 else ""
        if sub == "eventimages":
            return "mwecau/events"
        if sub == "gallery":
            if len(parts) > 2 and parts[2].lower() == "thumbnail":
                return "mwecau/gallery/thumbnails"
            return "mwecau/gallery"
        return "mwecau/pages"

    return "mwecau/misc"

def main():
    files = []
    search_dirs = [
        ROOT / "mw_web" / "img",
        ROOT / "mw_web" / "images",
    ]
    for d in search_dirs:
        if d.exists():
            for p in sorted(d.rglob("*")):
                if p.is_file() and p.suffix in EXTENSIONS:
                    files.append(p)

    print(f"Found {len(files)} images\n")

    mapping = {}
    for path in files:
        cf = get_folder(path)
        public_id = f"{cf}/{path.stem}"
        local_key = str(path.relative_to(ROOT / "mw_web"))
        # Mock URL (same format as real Cloudinary)
        cdn_url = f"https://res.cloudinary.com/diucc3vyb/image/upload/f_auto,q_auto/{public_id}"
        mapping[local_key] = cdn_url
        print(f"  {local_key:50s} → …/{public_id}")

    map_path = ROOT / "scripts" / "cloudinary_map.json"
    with open(map_path, "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"\n✅ Mock mapping saved: {map_path}")
    print(f"\nTo use REAL Cloudinary URLs later:")
    print(f"  1. Run: python scripts/upload_images.py")
    print(f"  2. Run: python scripts/replace_paths.py")

if __name__ == "__main__":
    main()
