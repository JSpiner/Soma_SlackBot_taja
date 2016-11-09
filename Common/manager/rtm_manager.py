#-*- coding: utf-8 -*-
import sys 
sys.path.append("../../Bot")

from Common.manager.redis_manager import redis_client
import Common.static
from multiprocessing import Process
from rtm import *

#rtm socket manager

def start_rtm(teamId):
    return 0 
    
def is_socket_opened(teamId):
    if redis_client.exists('rtm_status_'+teamId) == False:
        return static.SOCKET_STATUS_IDLE
    status = redis_client.hget('rtm_status_'+teamId, 'status')
    return status

# 반듯이 해당 함수 호출 전 소켓이 닫혀있는지 확인 필요 
def open_new_socket(teamId, data):
    process = Process(target = open_socket, args=(teamId,data))
    process.start()
    return 0
