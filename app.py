from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def get_productos():
    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    productos = conn.execute(
        "SELECT * FROM productos"
    ).fetchall()

    conn.close()

    return productos


@app.route("/")
def home():
    productos = get_productos()

    return render_template(
        "index.html",
        productos=productos
    )


if __name__ == "__main__":
    app.run(debug=True)