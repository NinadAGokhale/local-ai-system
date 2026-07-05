#!/Users/ninadgokhale/anaconda3/bin/python3
import os, sys
sys.path.insert(0, '/Users/ninadgokhale/Desktop/local-ai-system')
os.chdir('/Users/ninadgokhale/Desktop/local-ai-system')
from waitress import serve
from src.web.dashboard import app
serve(app, host='127.0.0.1', port=5002)
