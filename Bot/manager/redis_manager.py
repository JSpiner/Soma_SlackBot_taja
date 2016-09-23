# #-*- coding: utf-8 -*-
import redis
import json
with open('conf.json') as json_data:
    data = json.load(json_data)


def redisConnection():
	client = redis.StrictRedis(host=data["redis"]["host"],port=6379,db=0)	
	return client
