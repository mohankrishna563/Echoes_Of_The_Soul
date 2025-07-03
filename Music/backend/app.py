from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True)

SPOTIFY_CLIENT_ID = "b2483c60e08f4719ab6687bb068d60fe"
SPOTIFY_CLIENT_SECRET = "ad3e6d2aebe64f219bc83fc3f8cd7568"

VALID_USERS = {
    "ajay@gmail.com": "1234"  # Add more users dynamically later
}

def get_access_token():
    try:
        auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print("❌ Error getting Spotify token:", e)
        return None

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if VALID_USERS.get(email) == password:
        session["user"] = {"email": email}
        return jsonify({"message": "Login successful", "success": True}), 200
    return jsonify({"message": "Invalid credentials", "success": False}), 401

@app.route("/api/user")
def get_user():
    user = session.get("user")
    if user:
        return jsonify(user)
    return jsonify({"error": "User not logged in"}), 401


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if email in VALID_USERS:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    import re
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$', password):
        return jsonify({
            "success": False,
            "message": "Password must be 8+ chars with a number and special character"
        }), 400

    VALID_USERS[email] = password
    return jsonify({"success": True, "message": "Account created successfully"}), 200

@app.route("/api/search")
def search_mixed_results():
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Query required"}), 400

        access_token = get_access_token()
        if not access_token:
            return jsonify({"error": "Spotify access token missing"}), 500

        url = f"https://api.spotify.com/v1/search?q={query}&type=playlist&limit=30"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({
                "error": "Spotify API error",
                "details": response.text
            }), 500

        data = response.json()
        playlists = data.get("playlists", {}).get("items", [])

        results = []
        for item in playlists:
            if not item:
                continue
            results.append({
                "type": "playlist",
                "name": item.get("name", "Untitled"),
                "image": item.get("images", [{}])[0].get("url", ""),
                "embed": f"https://open.spotify.com/embed/playlist/{item.get('id', '')}"
            })

        return jsonify(results)

    except Exception as e:
        print("❌ Search API error:", str(e))
        return jsonify({
            "error": "Internal search error",
            "details": str(e)
        }), 500





if __name__ == "__main__":
    app.run(debug=True, port=5000)
