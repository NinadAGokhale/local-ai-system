"""Thin wrapper — delegates to src/web/dashboard.py Flask app."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web.dashboard import app

if __name__ == "__main__":
    print("Dashboard starting at http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
