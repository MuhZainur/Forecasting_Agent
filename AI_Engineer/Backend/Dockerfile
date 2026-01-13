# AI Chat Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure .env is handled (will be mounted or passed via docker-compose usually, but file exists securely now)
# We don't COPY .env explicitly if we want to rely on docker-compose env_file, 
# BUT current code architecture assumes file existence for python-dotenv.
# We will rely on docker volume mounting or COPY for now since it is secure in .env.
# COPY .env . 

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

EXPOSE 8005

CMD ["python", "run_chat_server.py"]
