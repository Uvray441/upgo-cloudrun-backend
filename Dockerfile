# Use a slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Cloud Run expects the app to listen on port 8080
EXPOSE 8080

# Run the app
CMD ["python", "main.py"]
