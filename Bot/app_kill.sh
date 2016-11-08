kill -9 `ps aux | grep gunicorn | awk '{print $2}'`
