#!/bin/bash
cd "$(dirname "$0")"
echo "──────────────────────────────────────────────"
echo "  Starting local web server for Moodscape...  "
echo "──────────────────────────────────────────────"

# Kill any existing process running on port 8000
lsof -ti :8000 | xargs kill -9 2>/dev/null

# Start python's built-in HTTP server in the background
python3 -m http.server 8000 &
SERVER_PID=$!

# Wait briefly for the server to spin up
sleep 1

# Open the app in the default web browser
open http://localhost:8000/index.html

echo ""
echo "👉 Web app is now running at: http://localhost:8000/"
echo "👉 Press [Control + C] in this window to stop the server."
echo ""

# Keep terminal alive until the user stops it
wait $SERVER_PID
