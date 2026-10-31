from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

CSV_PATH = Path(__file__).parent / "data" / "TUJ_Spring2027_Courses.csv"

@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/app/health")
def health():

    csv_ok = CSV_PATH.exists()

    if csv_ok:
        return jsonify(status="ok", catalog="found"), 200
    else:
        return jsonify(status="error", catalog="missing"), 503
    
if __name__ == '__main__':
    app.run(debug=True, port=8000)
