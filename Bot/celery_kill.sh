kill -9 `ps aux | grep celery | awk '{print $2}'`
