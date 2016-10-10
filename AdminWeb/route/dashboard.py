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
class DashBoards(MethodView):

    def get(self, types):
        if types == "getIndicator":
            
            try:

                print("[DashBoard]_GETINDICATOR")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "select count(*) as todayInstalle from TEAM WHERE DATE(TEAM.team_joined_time) = CURDATE()"
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                print(rows)
                print(rows[0]["todayInstalle"])

                data = {}
                data["todayInstalle"] = rows[0]["todayInstalle"]
                print(data)
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        
    
    def post(self,types):
        print("post")
        # hashKey = request.form['hashKey']                

       