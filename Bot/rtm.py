from slackclient import SlackClient

from celery_worker import worker
import Common.test as tester
import requests
import json
import time
import sqlalchemy
from Common.manager import redis_manager
from Common.manager import db_manager
from Common import static
import datetime
from Common import util
from Common.static import *
import time
import base64
import datetime

def open_new_socket(teamId):

    redis_manager.redis_client.hset('rtm_status_'+teamId, 'status', SOCKET_STATUS_CONNECTING)
    redis_manager.redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + SOCKET_EXPIRE_TIME)

    result = db_manager.query(
        "SELECT team_bot_access_token "
        "FROM TEAM "
        "WHERE "
        "team_id = %s "
        "LIMIT 1",
        (teamId, )
    )
    bot_token = util.fetch_all_json(result)[0]['team_bot_access_token']
    _connect(teamId, bot_token)

def _connect(teamId, bot_token):
    sc = SlackClient(token)
    if sc.rtm_connect():
        print("connected! : " + teamId)
   
        redis_manager.redis_client.hset('rtm_status_'+teamId, 'status', SOCKET_STATUS_CONNECTED)
        redis_manager.redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + SOCKET_EXPIRE_TIME)

        while True:
            response = sc.rtm_read()

            if len(response) == 0:  
                continue

            # response는 배열로, 여러개가 담겨올수 있음
            for data in response:
                print(data)

                try:
                    if data['type'] == "message":

                        data['team_id'] = data['team']
                        status_channel = redis_manager.redis_client.get("status_" + data["channel"])
                        
                        # 게임이 플레이중이라면
                        if status_channel == static.GAME_STATE_PLAYING :
                            print('playing')
                            worker.delay(data)

                except Exception as e:
                    print('error ' + str(e))
    else:
        print("connection failed!")
        
        redis_manager.redis_client.hset('rtm_status_'+teamId, 'status', SOCKET_STATUS_RECONNECTING)
        
        time.sleep(3)
        _connect(teamId, bot_token)

    return 0
