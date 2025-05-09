from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # TEMP: Allow all origins during development

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Server is running!"})

@app.route("/rune-convert", methods=["POST", "OPTIONS"])
def rune_converter():
    if request.method == "OPTIONS":
        return '', 204

    data = request.json
    rune_slug = data.get("runeSlug")
    usd_price = float(data.get("usdPrice", 0))

    if not rune_slug or not usd_price:
        return jsonify({"error": "Missing runeSlug or usdPrice"}), 400

    try:
        me_response = requests.get(
            f"https://runes-api.magiceden.dev/v1/runes/token/{rune_slug}",
            headers={"Authorization": "Bearer YOUR_API_KEY_HERE"}
        )

        if me_response.status_code != 200:
            return jsonify({"error": "Failed to fetch Rune data", "details": me_response.text}), 502

        rune_data = me_response.json()
        rune_btc = float(rune_data.get("lastSalePriceInBtc"))

        btc_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        btc_price = btc_res.json()["bitcoin"]["usd"]

        btc_needed = usd_price / btc_price
        runes_needed = btc_needed / rune_btc

        return jsonify({
            "runeSlug": rune_slug,
            "usdPrice": usd_price,
            "btcPriceUSD": btc_price,
            "runeLastSaleBTC": rune_btc,
            "estimatedRunes": round(runes_needed, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
