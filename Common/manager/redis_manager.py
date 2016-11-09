# #-*- coding: utf-8 -*-

import redis
import json
with open('../conf.json') as conf_json:
    conf = json.load(conf_json)

redis_client = redis.StrictRedis(host=conf["redis"]["host"],port=6379,db=0,charset="utf-8", decode_responses=True)	
