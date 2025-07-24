import os
import subprocess
import tempfile
import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {
      'storageBucket': 'upgo-441.firebasestorage.app'
})

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'zip_file' not in request.files or 'build_type' not in request.form:
        return jsonify({'error': 'Missing file or build type'}), 400

    zip_file = request.files['zip_file']
    build_type = request.form['build_type']  # "apk" or "aab"
    filename = secure_filename(zip_file.filename)

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, filename)
    zip_file.save(zip_path)

    try:
        # Unzip
        unzip_dir = os.path.join(temp_dir, "unzipped")
        os.makedirs(unzip_dir)
        subprocess.run(['unzip', zip_path, '-d', unzip_dir], check=True)

                # Build
        gradlew_path = os.path.join(unzip_dir, 'gradlew')
        if not os.path.exists(gradlew_path):
            return jsonify({'error': 'gradlew not found'}), 400

        os.chmod(gradlew_path, 0o755)
        
        # ⚠️ Change: Always use DEBUG build (not Release)
        build_cmd = ['./gradlew', 'bundleDebug'] if build_type == 'aab' else ['./gradlew', 'assembleDebug']
        subprocess.run(build_cmd, cwd=unzip_dir, check=True)

        # Find output
        build_output_path = ''
        if build_type == 'apk':
            for root, dirs, files in os.walk(unzip_dir):
                for f in files:
                    if f.endswith('.apk'):
                        build_output_path = os.path.join(root, f)
                        break
        else:
            for root, dirs, files in os.walk(unzip_dir):
                for f in files:
                    if f.endswith('.aab'):
                        build_output_path = os.path.join(root, f)
                        break

        if not build_output_path:
            return jsonify({'error': 'Build output not found'}), 500

        # Upload to Firebase
        bucket = storage.bucket()
        blob = bucket.blob(os.path.basename(build_output_path))
        blob.upload_from_filename(build_output_path)
        blob.make_public()

        return jsonify({'download_url': blob.public_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
