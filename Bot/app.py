# #-*- coding: utf-8 -*-
# from celery_worker import worker

# worker.delay(random.randint(0,100))

from slackclient import SlackClient

from manager import db_manager
from manager import redis_manager
from common import static

import time
import json
with open('conf.json') as json_data:
    data = json.load(json_data)

# print(static.REDIS_GAME_STATUS)

redis = redis_manager.redisConnection()
db = db_manager.sqlConnection()
bot = SlackClient(data["slack"]["botKey"])



if bot.rtm_connect():
    
    data = bot.rtm_read()

    while True:
        	
        	data = bot.rtm_read()


	        if len(data) == 0:	        
	        	pass

			# 데이터가 무언가 있을떄
	        else:
			
	        	#게임이 시작되었나 확인하고
	        	#게임이 시작되있지 않다면.
	        	game_status = redis.get(static.REDIS_GAME_STATUS);
	        	print(data[0])
	        	# none 이거나 game End일경우에는 .start 등의 명령어가 가능하도록.
        		if game_status == None or game_status == static.REDIS_GAME_END:
					
        			print('no Playing')	        		
					# 데이터가 있다면 항상 타입이 존재한다.        		
	        		typee = data[0]["type"]
	        	        	
	        		# .시작일경우
	        		if typee == 'message' and data[0]["text"] == static.STR_GAME_START:
	        			print('.start')
	        			pass 
	        		#  아무것도 안한다고 pass를 안해주면. 어디서 블락되었는지 알지 못한다. =>syntax err
	        		else:
	        			pass
	        	#게임중일경우. 제시어를 받는다.
	        	elif game_status == static.REDIS_GAME_PLAYING:
	        		pass

	        	else:
	        		pass	
       
	        	pass
	        time.sleep(0.5)
else:
	print ("Connection Failed, invalid token?")





