#!/bin/bash
cd /Users/ninadgokhale/Desktop/local-ai-system
export PYTHONPATH="/Users/ninadgokhale/Desktop/local-ai-system:$PYTHONPATH"
exec /Users/ninadgokhale/anaconda3/bin/python3 -m waitress --port=5002 --host=127.0.0.1 src.web.dashboard:app
