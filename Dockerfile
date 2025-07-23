# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Cloud Run runs on 8080)
EXPOSE 8080

# Run the Flask app
CMD ["python", "main.py"]
