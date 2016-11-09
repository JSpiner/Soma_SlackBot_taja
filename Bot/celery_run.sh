#! /bin/bash
NEW_RELIC_CONFIG_FILE=../newrelic.ini newrelic-admin run-program celery -A celery_worker worker --loglevel=info
