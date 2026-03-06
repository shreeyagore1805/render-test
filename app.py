from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "players.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    data = load_data()
    return jsonify(data)


@app.route("/bid", methods=["POST"])
def bid():
    player = request.json.get("player")
    company = request.json.get("company")
    price = int(request.json.get("price"))

    data = load_data()

    if player not in data:
        data[player] = {"company": company, "price": price}
        save_data(data)
        return {"message": "Player added", "data": data[player]}

    current_price = data[player]["price"]

    if price > current_price:
        data[player] = {"company": company, "price": price}
        save_data(data)
        return {"message": "Bid updated", "data": data[player]}

    return {"message": "Bid must be higher than current price"}, 400


@app.route("/players")
def players():
    return jsonify(load_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

