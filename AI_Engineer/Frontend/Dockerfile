# Frontend Dockerfile (Development/Preview Mode)
FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Using --host to ensure container exposure
CMD ["npm", "run", "dev", "--", "--host"]
