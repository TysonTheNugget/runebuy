from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_url_path="", static_folder=".")
CORS(app)  # <-- this enables CORS for all routes

UNISAT_API_KEY = "bf4358eb9068258ccf5ae9049df5344d04d7f8fd6724b8ddf9185b7640d2006f"
TREASURY = "bc1pra6pu30zu5ux72fs0jryh2ykt2zdqkcc2t7n98rrjpy70mnm3fcsxgd9xy"
WEB3FORMS_KEY = "0d77267c-e8c1-4ded-98cb-f6e909a234d5"
MAGICEDEN_API_KEY = "6ed7b13e-063c-42fc-a27b-9bd87f8f7219"

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    transfer_data = {
        "toAddress": TREASURY,
        "rune": "WISHY•WASHY•MACHINE",
        "amount": "5000"
    }

    try:
        uni_response = requests.post(
            "https://open-api.unisat.io/v1/rune/transfer",
            headers={
                "Authorization": f"Bearer {UNISAT_API_KEY}",
                "Content-Type": "application/json"
            },
            json=transfer_data
        )

        print("\n📦 UniSat RAW RESPONSE:")
        print("STATUS:", uni_response.status_code)
        print("BODY:", uni_response.text)

        if uni_response.status_code != 200:
            return jsonify({
                "error": "UniSat rejected the request",
                "status_code": uni_response.status_code,
                "body": uni_response.text
            }), 500

        tx = uni_response.json()

        if "txid" not in tx:
            return jsonify({
                "error": "No txid returned from UniSat",
                "body": tx
            }), 400

        form_data = {
            "access_key": WEB3FORMS_KEY,
            "email": email,
            "subject": "Rune Purchase Complete",
            "name": email,
            "message": f"User {email} paid 5000 WISHY•WASHY•MACHINE runes.\nTXID: {tx['txid']}"
        }

        submit = requests.post("https://api.web3forms.com/submit", data=form_data)
        print("\n📧 Web3Forms RESPONSE:", submit.status_code, submit.text)

        if submit.status_code != 200:
            return jsonify({"error": "Web3Forms failed", "details": submit.text}), 400

        return jsonify({"success": True, "txid": tx["txid"]})

    except Exception as e:
        print("\n🔥 EXCEPTION:", str(e))
        return jsonify({"error": "Exception during transfer", "details": str(e)}), 500

@app.route("/rune-convert", methods=["POST"])
def rune_converter():
    data = request.json
    rune_slug = data.get("runeSlug")
    usd_price = float(data.get("usdPrice", 0))

    if not rune_slug or not usd_price:
        return jsonify({"error": "Missing runeSlug or usdPrice"}), 400

    try:
        # Get Rune info from Magic Eden
        me_response = requests.get(
            f"https://runes-api.magiceden.dev/v1/runes/token/{rune_slug}",
            headers={"Authorization": f"Bearer {MAGICEDEN_API_KEY}"}
        )

        if me_response.status_code != 200:
            return jsonify({"error": "Failed to fetch Rune data", "details": me_response.text}), 502

        rune_data = me_response.json()
        rune_btc = float(rune_data.get("lastSalePriceInBtc"))

        # Get current BTC price in USD
        btc_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        btc_price = btc_res.json()["bitcoin"]["usd"]

        # USD → BTC → Runes
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
        print("🔥 Error in rune-convert:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
