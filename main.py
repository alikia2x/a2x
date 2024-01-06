from flask import Flask, request, redirect, jsonify
import sqlite3, os
from dotenv import load_dotenv

app = Flask(__name__)
DATABASE = "links.db"
load_dotenv()


def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with app.open_resource("schema.sql", mode="r") as f:
                db.cursor().executescript(f.read())
            db.commit()


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.route("/", methods=["GET"])
def home():
    return redirect(os.getenv("HOME_PAGE"), code=307)

@app.route("/<id>", methods=["GET", "DELETE"])
def get_or_delete_link(id):
    if request.method == "GET":
        return get_link(id)
    elif request.method == "DELETE":
        return delete_link(id)


def get_link(id):
    db = get_db()
    link = db.execute("SELECT * FROM links WHERE id = ?", (id,)).fetchone()
    db.close()

    if link:
        return redirect(link["url"])
    else:
        return jsonify({"error": "Link not found"}), 404


def delete_link(id):
    db = get_db()
    db.execute("DELETE FROM links WHERE id = ?", (id,))
    db.commit()
    db.close()

    return jsonify({"message": "Link deleted successfully"}), 200


@app.route("/<id>", methods=["PATCH", "POST"])
def update_or_create_link(id):
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    if request.method == "PATCH":
        return update_link(id, url)
    elif request.method == "POST":
        return create_link(id, url)


def update_link(id, url):
    db = get_db()
    db.execute("UPDATE links SET url = ? WHERE id = ?", (url, id))
    db.commit()
    db.close()

    return jsonify({"message": "Link updated successfully"}), 200


def create_link(id, url):
    db = get_db()
    db.execute("INSERT INTO links (id, url) VALUES (?, ?)", (id, url))
    db.commit()
    db.close()

    return jsonify({"message": "Link created successfully"}), 201


if __name__ == "__main__":
    init_db()
    from gevent import pywsgi
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()
