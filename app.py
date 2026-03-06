from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

DATABASE = "players.db"
CSV_FILE = "ipl_auction.csv"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        team TEXT,
        base_price INTEGER,
        current_bid INTEGER,
        company TEXT
    )
    """)

    conn.commit()
    conn.close()


def load_dataset():
    conn = get_db()

    count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]

    if count == 0:

        df = pd.read_csv(CSV_FILE)

        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():

            name = row.get("Name","Unknown")
            team = row.get("TeamName","Unknown")
            base = row.get("BasePrices in Rs",0)

            conn.execute(
                "INSERT INTO players(name, team, base_price, current_bid, company) VALUES (?,?,?,?,?)",
                (name, team, base, base, "")
            )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    players = conn.execute("SELECT * FROM players ORDER BY current_bid DESC").fetchall()
    conn.close()

    return render_template("index.html", players=players)


@app.route("/bid", methods=["POST"])
def bid():
    player_id = request.form["player_id"]
    company = request.form["company"]
    bid_price = int(request.form["price"])

    conn = get_db()

    player = conn.execute(
        "SELECT current_bid FROM players WHERE id=?",
        (player_id,)
    ).fetchone()

    if bid_price > player["current_bid"]:

        conn.execute(
            "UPDATE players SET current_bid=?, company=? WHERE id=?",
            (bid_price, company, player_id)
        )

        conn.commit()

    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    load_dataset()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

