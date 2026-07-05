#!/usr/bin/env python3
"""Entry point for Saratthya — runs from anywhere with: python src/main.py"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.dashboard import app


def main():
    print("Dashboard starting at http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)


if __name__ == "__main__":
    main()
