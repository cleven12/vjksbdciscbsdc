"""
Replace local image paths in HTML and CSS files with Cloudinary CDN URLs.

Reads cloudinary_map.json produced by upload_images.py, then rewrites:
  - mw_web.html          (references like  images/..., img/...)
  - mw_web/academics.html
  - mw_web/campus-life.html
  - mw_web/gallery.html
  - mw_web/gallery/single/1.html
  - mw_web/University examinations/event.html
  - mw_web/css/style.css (url(../img/...) etc.)

The mapping keys are relative to mw_web/, e.g. "img/mwecau.png".
HTML files at root (mw_web.html) reference images as "img/..." or "images/..."
HTML files inside mw_web/ reference them as "img/..." or "images/..." (same).
CSS files inside mw_web/css/ reference them as "../img/..." — we strip the "../".
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAP_PATH = ROOT / "scripts" / "cloudinary_map.json"

# Files to process and their location (affects path prefix stripping)
FILES = [
    ROOT / "mw_web.html",
    ROOT / "mw_web" / "academics.html",
    ROOT / "mw_web" / "campus-life.html",
    ROOT / "mw_web" / "gallery.html",
    ROOT / "mw_web" / "gallery" / "single" / "1.html",
    ROOT / "mw_web" / "University examinations" / "event.html",
    ROOT / "mw_web" / "css" / "style.css",
    ROOT / "mw_web" / "css" / "gallery.css",
]


def load_map() -> dict[str, str]:
    with open(MAP_PATH) as f:
        return json.load(f)


def normalize_key(raw: str) -> str:
    """Strip leading ../ and ./ so the key matches the mapping format."""
    raw = raw.lstrip("./")
    if raw.startswith("../"):
        raw = raw[3:]
    return raw


def replace_in_file(file_path: Path, mapping: dict[str, str]) -> int:
    if not file_path.exists():
        print(f"  SKIP (not found): {file_path}")
        return 0

    text = file_path.read_text(encoding="utf-8")
    original = text
    replacements = 0

    for local_key, cdn_url in mapping.items():
        # Match the key with optional leading ../ or ./
        patterns = [
            local_key,
            f"../{local_key}",
            f"./{local_key}",
            local_key.replace(" ", "%20"),
            f"../{local_key.replace(' ', '%20')}",
            local_key.replace(" ", "&#32;"),  # HTML entity for space
            f"../{local_key.replace(' ', '&#32;')}",
        ]
        for pat in patterns:
            if pat in text:
                text = text.replace(pat, cdn_url)
                replacements += 1

    if text != original:
        file_path.write_text(text, encoding="utf-8")

    return replacements


def main():
    if not MAP_PATH.exists():
        print(f"ERROR: {MAP_PATH} not found. Run upload_images.py first.")
        return

    mapping = load_map()
    print(f"Loaded {len(mapping)} URL mappings\n")

    total = 0
    for fp in FILES:
        count = replace_in_file(fp, mapping)
        rel = fp.relative_to(ROOT)
        print(f"  {count:3d} replacements — {rel}")
        total += count

    print(f"\nTotal replacements: {total}")


if __name__ == "__main__":
    main()
