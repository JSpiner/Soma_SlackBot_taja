#! /bin/bash
NEW_RELIC_CONFIG_FILE=../newrelic_celery.ini newrelic-admin run-program nohup celery -A celery_worker worker --loglevel=info


