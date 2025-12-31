#!/bin/sh

# Generate config.js from Environment Variables
echo "window.config = {" > /app/dist/config.js
echo "  VITE_API_URL: '$VITE_API_URL'," >> /app/dist/config.js
echo "  VITE_DA_API_URL: '$VITE_DA_API_URL'" >> /app/dist/config.js
echo "};" >> /app/dist/config.js

# Start the server
exec serve -s dist -l 5173
