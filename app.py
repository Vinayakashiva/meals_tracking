"""
app.py — Flask version of the Hackathon Meals Register.

Run locally:
    pip install -r requirements.txt
    export GOOGLE_SERVICE_ACCOUNT_EMAIL=...
    export GOOGLE_PRIVATE_KEY=...
    export GOOGLE_SHEET_ID=...
    python app.py

Then open http://localhost:5000
"""

import os

from flask import Flask, jsonify, request, send_from_directory

from _sheets import get_team_members, set_meal

# Optional: load a local .env file if python-dotenv is installed (dev convenience only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/team", methods=["GET"])
def team():
    team_id = (request.args.get("team_id", "") or "").strip()

    if not team_id:
        return jsonify({"error": "team_id is required"}), 400

    try:
        team_data = get_team_members(team_id)
    except Exception as err:
        app.logger.exception("Failed to fetch team")
        return jsonify({"error": str(err) or "Server error"}), 500

    if not team_data["members"]:
        return jsonify({"error": f"No team found with ID '{team_id}'"}), 404

    return jsonify(team_data)


@app.route("/api/mark", methods=["POST"])
def mark():
    body = request.get_json(silent=True) or {}

    row = body.get("row")
    meal = body.get("meal")
    taken = bool(body.get("taken"))

    if not row:
        return jsonify({"error": "row is required"}), 400
    if meal not in ("lunch", "tiffin"):
        return jsonify({"error": "meal must be 'lunch' or 'tiffin'"}), 400

    try:
        set_meal(row, meal, taken)
    except Exception as err:
        app.logger.exception("Failed to mark meal")
        return jsonify({"error": str(err) or "Server error"}), 500

    return jsonify({"ok": True, "row": row, "meal": meal, "taken": taken})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
