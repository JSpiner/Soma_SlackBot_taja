#-*- coding: utf-8 -*-
import sys 
sys.path.append("../../Bot")

from redis_manager import redis_client
from multiprocessing import Process

#rtm socket manager

def start_rtm(teamId):
    return 0
    
def _is_socket_opened(teamId):
    if redis_client.exists('rtm_status_'+teamId) == False:
        return False
    status = redis_client.hget('rtm_status_'+teamId, 'status')
    return status

def test(index):
    print(i)

# 반듯이 해당 함수 호출 전 소켓이 닫혀있는지 확인 필요 
def _open_new_socket(teamId):
    process = Process(target=test, args=(teamId,))
    process.start()
    return 0

for i in range(0,10):
    _open_new_socket(i)
