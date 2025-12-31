# Frontend Dockerfile (Production Build)
FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Build for production
RUN npm run build

# Install lightweight static server
RUN npm install -g serve

# Create startup script for Runtime Environment Variables
RUN echo "#!/bin/sh" > start.sh && \
    echo "echo \"window.config = { VITE_API_URL: '\$VITE_API_URL', VITE_DA_API_URL: '\$VITE_DA_API_URL' };\" > /app/dist/config.js" >> start.sh && \
    echo "serve -s dist -l 5173" >> start.sh && \
    chmod +x start.sh

EXPOSE 5173

# Run the startup script
CMD ["./start.sh"]
