from redis_manager import redis_client
 #rtm socket manager

 def start_rtm(teamId):
     return 0
    
def _is_socket_opened(teamId):
    redis_client.get()
    return False

def _open_new_socket(teamId):
    return 0