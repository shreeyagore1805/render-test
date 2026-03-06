from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

DB = "players.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS players (
        name TEXT PRIMARY KEY,
        company TEXT,
        price INTEGER
    )
    """)
    conn.commit()
    conn.close()


def get_players():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    players = c.fetchall()
    conn.close()
    return players


@app.route("/")
def home():
    players = get_players()
    return render_template("index.html", players=players)


@app.route("/bid", methods=["POST"])
def bid():
    player = request.form["player"]
    company = request.form["company"]
    price = int(request.form["price"])

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT price FROM players WHERE name=?", (player,))
    result = c.fetchone()

    if result is None:
        c.execute("INSERT INTO players VALUES (?, ?, ?)", (player, company, price))

    elif price > result[0]:
        c.execute("UPDATE players SET company=?, price=? WHERE name=?", (company, price, player))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
