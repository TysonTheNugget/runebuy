from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow *everything* during development
CORS(app, origins="*", allow_headers="*", methods="*")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Server is running!"})

@app.route("/rune-convert", methods=["POST", "OPTIONS"])
def rune_convert():
    if request.method == "OPTIONS":
        # Flask-CORS will auto-attach headers
        return '', 204

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Fake response just to test
    return jsonify({
        "runeSlug": data.get("runeSlug"),
        "usdPrice": data.get("usdPrice"),
        "btcPriceUSD": 60000,
        "runeLastSaleBTC": 0.00001,
        "estimatedRunes": 2.5
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
