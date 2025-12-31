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

# Copy startup script
COPY generate_config.sh /app/generate_config.sh
RUN chmod +x /app/generate_config.sh

EXPOSE 5173

# Run the startup script
CMD ["/app/generate_config.sh"]
