#!/bin/bash
# Serves this folder so the editor can autosave, then opens it.
cd "$(dirname "$0")"
python3 -m http.server 8731 >/dev/null 2>&1 &
sleep 1
open "http://localhost:8731/editor.html"
echo "Editor running at http://localhost:8731/editor.html"
echo "Close this window when you're done."
wait
