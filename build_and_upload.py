from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/build", methods=["POST"])
def build_apk():
    # এখানে project zip file unzip করে apk build করা হবে
    return jsonify({"message": "APK build process started!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
