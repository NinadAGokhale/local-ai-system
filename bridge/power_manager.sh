#!/bin/bash
# Power Manager — keeps MacBook awake during WhatsApp bot operation

CMD="caffeinate -dimsu"

case "${1:-start}" in
  start)
    echo "Starting caffeinate to prevent sleep..."
    $CMD &
    CAFFEINATE_PID=$!
    echo $CAFFEINATE_PID > /tmp/.caffeinate_pid
    echo "caffeinate running (PID: $CAFFEINATE_PID)"
    ;;
  stop)
    if [ -f /tmp/.caffeinate_pid ]; then
      PID=$(cat /tmp/.caffeinate_pid)
      kill $PID 2>/dev/null
      rm /tmp/.caffeinate_pid
      echo "caffeinate stopped"
    else
      pkill caffeinate 2>/dev/null && echo "caffeinate stopped" || echo "caffeinate not running"
    fi
    ;;
  status)
    if pgrep caffeinate > /dev/null; then
      echo "caffeinate is running — system will not sleep"
    else
      echo "caffeinate is not running — system may sleep"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
