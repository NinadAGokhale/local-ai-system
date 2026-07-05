#!/usr/bin/env bash
set -euo pipefail

DIR="/Users/ninadgokhale/Desktop/local-ai-system"
ACTION="${1:-status}"

case "$ACTION" in
  start)
    launchctl load "$HOME/Library/LaunchAgents/com.saratthya.flask.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.saratthya.nport.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.saratthya.caffeinate.plist"
    echo "Saratthya started"
    ;;
  stop)
    launchctl unload "$HOME/Library/LaunchAgents/com.saratthya.flask.plist"
    launchctl unload "$HOME/Library/LaunchAgents/com.saratthya.nport.plist"
    launchctl unload "$HOME/Library/LaunchAgents/com.saratthya.caffeinate.plist"
    echo "Saratthya stopped"
    ;;
  status)
    echo "=== Flask app ==="
    launchctl list | grep saratthya.flask || echo "  not running"
    echo "=== Tunnel ==="
    launchctl list | grep saratthya.nport || echo "  not running"
    echo "=== Caffeinate ==="
    launchctl list | grep saratthya.caffeinate || echo "  not running"
    echo "=== URL ==="
    echo "  https://saratthya-agentic.nport.link"
    ;;
  url)
    echo "https://saratthya-agentic.nport.link"
    ;;
  restart)
    "$0" stop
    sleep 2
    "$0" start
    ;;
  *)
    echo "Usage: $0 {start|stop|status|url|restart}"
    exit 1
    ;;
esac
