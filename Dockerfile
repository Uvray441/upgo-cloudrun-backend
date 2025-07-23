FROM openjdk:17-slim

# unzip, curl, gradle, git, python install korte hobe
RUN apt-get update && apt-get install -y unzip curl git python3-pip zip && \
    apt-get clean

# firebase-admin install
RUN pip3 install firebase-admin flask

# App directory create
WORKDIR /app

# All files copy
COPY . .

# Ensure permissions for gradlew
RUN chmod +x /app/gradlew || true

# Port expose
EXPOSE 8080

# Run backend
CMD ["python3", "main.py"]
