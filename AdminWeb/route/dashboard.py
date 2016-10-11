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

                data = {}

                print("[DashBoard]_GETINDICATOR")            
                conn = db_manager.engine.connect()
                todayInstall = conn.execute(
                    "select count(*) as todayInstall from TEAM WHERE DATE(TEAM.team_joined_time) = CURDATE()"
                )
                todayPlay = conn.execute(
                    "select count(*) as todayPlay from GAME_INFO WHERE DATE(GAME_INFO.start_time) = CURDATE()"
                )
                inActiveUsers = conn.execute(
                    "select gr.user_id as userId,Max(gi.end_time) as recentTime, Max(gi.end_time)<DATE_SUB(CURDATE() , INTERVAL 7 DAY) as isInActive from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id group by gr.user_id"
                )
                inActiveTeams = conn.execute(
                    "select team_id,gameTotal,inActiveGameTotal,gameTotal=inActiveGameTotal as isInActive from"
                    "(select gi.team_id as team_id,("
                    "select count(*) from GAME_INFO where team_id in( "
                    "select team_id from GAME_INFO where team_id =gi.team_id"
                    ")"
                    ") AS gameTotal,count(*) as inActiveGameTotal"
                    " from GAME_INFO as gi where gi.end_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY)   group by gi.team_id) as sub"
                )

                conn.close()
                row_todayInstall = util.fetch_all_json(todayInstall)                
                row_todayPlay = util.fetch_all_json(todayPlay)                
                row_inActiveUsers = util.fetch_all_json(inActiveUsers)                
                row_inActiveTeams = util.fetch_all_json(inActiveTeams)                
                # print(row_inActiveUsers)
                # print(row_inActiveUsers)

                team_inActiveSum = 0
                for row in row_inActiveTeams:
                    team_inActiveSum = team_inActiveSum + int(row["isInActive"])

                user_inActiveSum = 0
                for row in row_inActiveUsers:
                    user_inActiveSum = user_inActiveSum + int(row["isInActive"])

                # print(team_inActiveSum)


                data["todayInstall"] = row_todayInstall[0]["todayInstall"]
                data["todayPlay"] = row_todayPlay[0]["todayPlay"]
                data["inActiveUsers"] = user_inActiveSum
                data["inActiveTeams"] = team_inActiveSum
                
                return json.dumps(static.RES_DEFAULT(200,data),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        
    
    def post(self,types):
        print("post")
        # hashKey = request.form['hashKey']                

       