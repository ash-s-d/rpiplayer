#! /bin/sh
# /etc/init.d/uwsgi
#

USER=www-data

UWSGI_NAME=uwsgi
UWSGI_BIN=/usr/local/bin/uwsgi
PYTHON_PATH=/usr/local/lib/python2.7/dist-packages

SOCKET_FILE=/tmp/webapp.sock
PID_FILE=/tmp/webapp.pid

PYTHON_APP_DIR=/opt/rpiplayer/
PYTHON_SCRIPT=rpiplayerw.py

case "$1" in
  start)
    if [ ! -f $PID_FILE ]
    then
      echo "Starting uwsgi"

      sudo -u $USER $UWSGI_BIN --pythonpath $PYTHON_PATH --chdir $PYTHON_APP_DIR --socket $SOCKET_FILE --wsgi-file $PYTHON_APP_DIR$PYTHON_SCRIPT > /dev/null 2>&1 &

      echo $! > $PID_FILE
    else
      echo "PID file "$PID_FILE" exists! process already running?"
    fi
    ;;
  stop)
    if [ ! -f $PID_FILE ]
    then
      echo "PID file "$PID_FILE" does not exist! Verify if process is already stopped."
    else
      rm $PID_FILE

      ps -ef | grep $UWSGI_NAME | awk '{print $2}' | xargs kill
    fi
    ;;
  *)
    echo "USAGE: /etc/init.d/uwsgi {start|stop}"
    
    exit 1
    
    ;;
esac

exit 0