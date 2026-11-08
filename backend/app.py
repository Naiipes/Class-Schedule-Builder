from pathlib import Path
from flask import Flask, jsonify, send_from_directory

from catalog.importer import CsvCatalogImporter
from catalog.repository import CatalogRepository
from routes.routes import api

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
CSV_PATH = BASE_DIR / "data" / "TUJ_Spring2027_Courses.csv"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

if CSV_PATH.exists():
    term = CsvCatalogImporter(CSV_PATH).load()
    app.config["REPO"] = CatalogRepository(term)

app.register_blueprint(api)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/health")
def health():
    if CSV_PATH.exists():
        return jsonify(status="ok", catalog="found"), 200
    return jsonify(status="error", catalog="missing"), 503

if __name__ == "__main__":
    app.run(debug=True, port=8000)