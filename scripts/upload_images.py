"""
Parallel image upload to Cloudinary (5 concurrent uploads).
Much faster than sequential uploads.
"""

import asyncio
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import cloudinary
import cloudinary.uploader
from decouple import config

ROOT = Path(__file__).parent.parent

cloudinary.config(
    cloud_name=config("API_NAME").strip(),
    api_key=config("API_KEY").strip(),
    api_secret=config("API_SECRET").strip(),
    secure=True,
)

EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".JPG", ".JPEG", ".PNG"}
MAX_WORKERS = 5  # Parallel uploads


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


def collect_images() -> list[Path]:
    search_dirs = [
        ROOT / "mw_web" / "img",
        ROOT / "mw_web" / "images",
    ]
    files = []
    for d in search_dirs:
        if d.exists():
            for p in sorted(d.rglob("*")):
                if p.is_file() and p.suffix in EXTENSIONS:
                    files.append(p)
    return files


def upload_image(path: Path) -> dict:
    """Upload a single image. Returns result or error dict."""
    cf = get_folder(path)
    public_id = f"{cf}/{path.stem}"
    local_key = str(path.relative_to(ROOT / "mw_web"))

    # Cloudinary will auto-add format, but we append extension for clarity
    ext = path.suffix.lower()
    if ext and not public_id.endswith(ext):
        public_id = f"{public_id}{ext}"

    try:
        resp = cloudinary.uploader.upload(
            str(path),
            public_id=public_id,
            overwrite=False,
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )
        return {
            "status": "ok",
            "file": path.name,
            "url": resp["secure_url"],
            "local": local_key,
        }
    except Exception as e:
        return {
            "status": "fail",
            "file": path.name,
            "local": local_key,
            "error": str(e),
        }


def main():
    files = collect_images()
    print(f"Found {len(files)} images. Starting parallel upload ({MAX_WORKERS} workers)...\n")

    results = []
    failed = []
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(upload_image, f) for f in files]

        for i, future in enumerate(futures, 1):
            result = future.result()

            if result["status"] == "ok":
                print(
                    f"[{i:02}/{len(files)}] ✓ {result['file']:50s} → {result['url']}"
                )
                results.append(result)
            else:
                print(f"[{i:02}/{len(files)}] ✗ {result['file']:50s} — {result['error']}")
                failed.append(result)

    print(f"\n✅ Done: {len(results)} uploaded, {len(failed)} failed")

    # Save mappings
    mapping_path = ROOT / "scripts" / "cloudinary_map.json"
    with open(mapping_path, "w") as f:
        json.dump({r["local"]: r["url"] for r in results}, f, indent=2)
    print(f"URL mapping saved → {mapping_path}")

    if failed:
        fail_path = ROOT / "scripts" / "cloudinary_failed.json"
        with open(fail_path, "w") as f:
            json.dump(failed, f, indent=2)
        print(f"Failed list saved → {fail_path}")


if __name__ == "__main__":
    main()
