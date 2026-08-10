import os
import json
from flask import Flask, render_template_string, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_JSON_PATH = os.path.join(BASE_DIR, "dashboard_data.json")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/index.css')
def css():
    return send_from_directory('.', 'index.css')

@app.route('/app.js')
def js():
    return send_from_directory('.', 'app.js')

@app.route('/dashboard_data.json')
@app.route('/api/dashboard')
def dashboard_data():
    if os.path.exists(DASHBOARD_JSON_PATH):
        try:
            with open(DASHBOARD_JSON_PATH, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"active_trades": [], "closed_trades": [], "summary": {}})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
