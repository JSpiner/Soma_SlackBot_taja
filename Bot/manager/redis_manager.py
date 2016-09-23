import redis
import json
with open('conf.json') as conf_json:
    conf = json.load(conf_json)

redis_client = redis.StrictRedis(
    conf["redis"]["host"],
    conf["redis"]["port"],
    conf["redis"]["db"])

