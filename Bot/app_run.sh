#! /bin/bash
NEW_RELIC_CONFIG_FILE=../newrelic.ini newrelic-admin run-program gunicorn -w8 --certfile=../../SSL_key/last.crt --keyfile=../../SSL_key/ssoma.key app:app -b 0.0.0.0:20000
