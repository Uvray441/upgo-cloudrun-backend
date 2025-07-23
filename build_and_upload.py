import os
import zipfile
import subprocess
import uuid
from flask import Flask, request, jsonify

# Firebase Admin SDK imports
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# Initialize Firebase Admin with service account
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'upgo-466814.appspot.com'  # আপনার Firebase Storage bucket নাম
})

@app.route("/")
def home():
    return "✅ Backend is running!"

@app.route("/build", methods=["POST"])
def build_apk():
    # 1) ফাইল আছে কিনা চেক
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    # 2) Build type (apk or aab)
    build_type = request.form.get("type", "apk").lower()
    if build_type not in ("apk", "aab"):
        return jsonify({"error": "Invalid build type"}), 400

    # 3) Unique ID generate
    build_id = str(uuid.uuid4())[:8]
    zip_filename = f"{build_id}.zip"

    # 4) Upload করা ZIP সেভ করা
    file = request.files['file']
    file.save(zip_filename)

    # 5) Unzip করার জন্য ডিরেক্টরি বানাও
    extract_dir = f"project_{build_id}"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_filename, 'r') as z:
        z.extractall(extract_dir)

    # 6) Gradle build চলাও
    gradlew = os.path.join(extract_dir, 'gradlew')
    os.chmod(gradlew, 0o755)
    cmd = [gradlew, 'bundleRelease'] if build_type == 'aab' else [gradlew, 'assembleRelease']
    result = subprocess.run(cmd, cwd=extract_dir, capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({
            "error": "Build failed",
            "details": result.stderr
        }), 500

    # 7) Output ফাইল খুঁজে বের করা
    output_file = None
    for root, dirs, files in os.walk(os.path.join(extract_dir, 'app', 'build', 'outputs')):
        for f in files:
            if build_type == 'apk' and f.endswith('.apk'):
                output_file = os.path.join(root, f)
                break
            if build_type == 'aab' and f.endswith('.aab'):
                output_file = os.path.join(root, f)
                break
        if output_file:
            break

    if not output_file:
        return jsonify({"error": "Output file not found"}), 500

    # 8) Firebase Storage এ আপলোড
    bucket = storage.bucket()
    remote_path = f"builds/{build_id}-{build_type}.{build_type}"
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(output_file)
    blob.make_public()
    download_url = blob.public_url

    # 9) ক্লিনআপ (ঐচ্ছিক, পরবর্তীতে cron দিয়ে চালাতে পারো)
    # os.remove(zip_filename)
    # shutil.rmtree(extract_dir)

    # 10) রেসপন্স পাঠাও
    return jsonify({
        "download_url": download_url,
        "build_id": build_id,
        "build_type": build_type
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
