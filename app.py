from flask import Flask, jsonify
from burn_tracker import get_total_burned

app = Flask(__name__)

@app.route("/api/burned", methods=["GET"])
def burned_tokens():
    """총 소각량을 반환하는 API"""
    return jsonify({"total_burned": get_total_burned()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
