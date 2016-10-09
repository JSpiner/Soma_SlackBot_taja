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
        if types == "getAllUser":
            
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

        elif types == "getGameResult":
            try:
                channel_id = request.args.get('channel_id')

                print("[ADMIN]getGameResult With channelID")    

                conn = db_manager.engine.connect()
                result = ""
                # print("channelID= "+channel_id)
                if channel_id == None :
                    result = conn.execute(
                        "SELECT * FROM GAME_RESULT "                        
                    )
                
                else :
                    result = conn.execute(
                        "SELECT GAME_RESULT.* FROM GAME_INFO "
                        "inner join GAME_RESULT on GAME_INFO.game_id = GAME_RESULT.game_id where GAME_INFO.channel_id = %s",
                        (channel_id)
                        )
                
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)
            
            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getAllTeam":

            try:

                print("[ADMIN]_GET_ALL team")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * FROM TEAM "
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getAllChannel":

            try:
                team_id = request.args.get('teamId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * FROM CHANNEL where  team_id=%s",
                    (team_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getAllGame":

            try:
                channel_id = request.args.get('channelId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * FROM GAMEINFO where  channel_id=%s",
                    (channel_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

    
    def post(self,types):
        print("post")
        # hashKey = request.form['hashKey']                

       