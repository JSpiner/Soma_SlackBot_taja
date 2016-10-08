import time
# Add a comment to this line

# current_milli_time = lambda: int(round(time.time() * 1000))
TIME_CURRENT = lambda: int(round(time.time() * 1000))
# defaultError = lambda err: {'error' : err}

# ERR_DEFAULT = lambda err: { 'code': 400, 'data' : err} 

RES_DEFAULT = lambda code,data: {'code' : code,'data' : data}
# defaultResponse = lambda code,data: {'code' : code,'data' : data}