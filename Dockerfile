FROM openjdk:17-slim

# Required packages
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    git \
    python3-pip \
    zip \
    wget \
    lib32stdc++6 \
    lib32z1 \
    && apt-get clean

# Install Firebase Admin + Flask
RUN pip3 install firebase-admin flask

# Set environment variables
ENV ANDROID_SDK_ROOT=/sdk
ENV ANDROID_HOME=/sdk
ENV PATH="${PATH}:/sdk/cmdline-tools/latest/bin:/sdk/platform-tools:/sdk/emulator:/sdk/build-tools/34.0.0"

# Install Android SDK Command Line Tools
RUN mkdir -p /sdk/cmdline-tools && \
    cd /sdk/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O tools.zip && \
    unzip tools.zip && \
    rm tools.zip && \
    mv cmdline-tools latest

# Accept all SDK licenses
RUN yes | sdkmanager --licenses

# Install platform-tools, build-tools and platform (adjust API level if needed)
RUN sdkmanager \
    "platform-tools" \
    "build-tools;34.0.0" \
    "platforms;android-34" \
    "emulator"

# Set working directory for android build
WORKDIR /android

# Copy android project only
COPY android-project/ /android/

# Make gradlew executable
RUN chmod +x ./gradlew

# Build APK (optional, or you can do it in main.py)
# RUN ./gradlew assembleDebug

# Set working directory for Flask backend
WORKDIR /app

# Copy backend code
COPY main.py .
COPY firebase_config.json .
COPY requirements.txt .

# Expose Flask port
EXPOSE 8080

# Run backend
CMD ["python3", "main.py"]
