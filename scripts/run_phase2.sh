#!/bin/bash
# Wait for Cloudinary upload to complete, then run path replacement

MAP_FILE="scripts/cloudinary_map.json"
MAX_WAIT=900  # 15 minutes
INTERVAL=5

echo "⏳ Waiting for Cloudinary upload to complete..."
ELAPSED=0

while [ ! -f "$MAP_FILE" ]; do
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "❌ Timeout: upload did not complete in ${MAX_WAIT}s"
        exit 1
    fi
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    if [ $((ELAPSED % 30)) -eq 0 ]; then
        echo "   ... waiting ($((ELAPSED/60))m elapsed)"
    fi
done

echo "✅ Cloudinary upload complete! Found $MAP_FILE"
echo ""
echo "Running path replacement..."
python scripts/replace_paths.py

echo ""
echo "✅ Done!"
echo ""
echo "Next: Test locally with:"
echo "  cd /home/cleven/Private/cleven-github/mw_web/cleven12.github.io"
echo "  python3 -m http.server 8080"
echo "Then open http://localhost:8080/mw_web.html"
