from flask.views import MethodView



import json
import time
from flask import request
from manager import db_manager

# from DBS import DBPool
# from utilz import util
from utilz import static
from utilz import util
import logging

# logging.basicConfig(filename='log.log',level=logging.DEBUG)

#For Memebers
class Members(MethodView):

    def get(self, types):
        if types == "getTest":            
            print("get!")
            return json.dumps(static.RES_DEFAULT(200,"data"),sort_keys=True, indent = 4)
    
    def post(self,types):
        print("post")
        if types == "all_user":
            
            try:

                print("[ADMIN]_GET_ALLUSER")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * FROM USER "
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        

