# auth_server.py
import os
import urllib

import jwt
import datetime
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv
load_dotenv()



MAIN_URL = os.getenv("MAIN_URL")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

CORS(app, supports_credentials=True, origins="*")

JWT_SECRET = "plantscapeinc"
JWT_EXPIRY = 60 * 60 * 24

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@app.route("/")
def index():
    return {"healthCheck": True, "MAIN_URL": MAIN_URL}


@app.route("/login")
def login():
    # redirect_uri = url_for("auth_callback", _external=True)
    redirect_uri = f"{MAIN_URL}/auth/callback"

    print(redirect_uri)
    return google.authorize_redirect(redirect_uri)


@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    resp = google.get("userinfo", token=token)
    user_info = resp.json()

    payload = {
        "sub": user_info["email"],
        "name": user_info["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRY),
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return redirect(f"{MAIN_URL}/account?token={jwt_token}")


@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    token = data.get("token")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({"valid": True, "payload": payload})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "invalid"}), 401


if __name__ == "__main__":
    app.run(port=5000, debug=True)
