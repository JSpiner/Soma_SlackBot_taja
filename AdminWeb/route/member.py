from flask.views import MethodView

import json
import time
from flask import request

# from DBS import DBPool
# from utilz import util
from utilz import static
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
            print("all_user")
            
            try:

                print("post")
                return json.dumps(static.RES_DEFAULT(200,"data"),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        

