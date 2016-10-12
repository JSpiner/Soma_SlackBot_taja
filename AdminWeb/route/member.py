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
                rows = util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)
            
            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getTeamInfo":
            try:
                teamId = request.args.get('teamId')

                print("[ADMIN]getTeamInfo With channelID")    

                conn = db_manager.engine.connect()
                result = ""
                # print("channelID= "+channel_id)
               
                result = conn.execute(
                    "SELECT *,  ( "
                    "    SELECT "
                    "        count(user_id) "
                    "    FROM USER  "
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as user_num, "
                    "( "
                    "    SELECT " 
                    "        count(team_id) "
                    "        FROM GAME_INFO "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as game_num, "
                    "( "
                    "    SELECT " 
                    "        AVG(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as avg_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as max_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(start_time) "
                    "        FROM GAME_INFO  "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as recent_play_time "
                    "from TEAM "
                    "where TEAM.team_id = %s; ",
                    teamId
                )
                
                conn.close()
                rows = util.fetch_all_json(result)                
                
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
                    "SELECT *,  ( "
                    "    SELECT "
                    "        count(user_id) "
                    "    FROM USER  "
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as user_num, "
                    "( "
                    "    SELECT " 
                    "        count(team_id) "
                    "        FROM GAME_INFO "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as game_num, "
                    "( "
                    "    SELECT " 
                    "        AVG(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as avg_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as max_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(start_time) "
                    "        FROM GAME_INFO  "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as recent_play_time "
                    "from TEAM ; "
                )
                conn.close()
                rows =util.fetch_all_json(result)       
                print(rows)         
                
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
                    "SELECT * ,"
                    "( "
                    "    SELECT "
                    "        MAX(start_time) "
                    "        FROM GAME_INFO "
                    "    WHERE "
                    "        GAME_INFO.channel_id = CHANNEL.channel_id "
                    ") as recent_play_time "
                    "FROM CHANNEL  "
                    "WHERE team_id = %s ",
                    (team_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getChannelInfo":

            try:
                channel_id = request.args.get('channelId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT CHANNEL.channel_id, CHANNEL.channel_name, CHANNEL.channel_joined_time,"
                    "( "
                    "    SELECT "
                    "        MAX(GAME_INFO.start_time) "
                    "        FROM GAME_INFO "
                    "    WHERE "
                    "        GAME_INFO.channel_id = CHANNEL.channel_id "
                    ") as recent_play_time "
                    "FROM CHANNEL  "
                    "WHERE channel_id = %s ",
                    (channel_id)
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
                    "SELECT * FROM GAME_INFO where  channel_id=%s",
                    (channel_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getAllGameResult":

            try:
                game_id = request.args.get('gameId')

                print("[ADMIN]_GET_ALL Games")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT user_name"
                    "    FROM USER"
                    "    WHERE"
                    "        USER.user_id = GAME_RESULT.user_id"
                    ") as user_name "
                    "FROM GAME_RESULT "
                    "WHERE   game_id=%s ",
                    (game_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getGameInfo":

            try:
                game_id = request.args.get('gameId')

                print("[ADMIN]_GET_ALL Games")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT count(user_id)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as user_num, "
                    "( "
                    "    SELECT MAX(score)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as max_score, "
                    "( "
                    "    SELECT AVG(score)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as avg_score, "
                    "( "
                    "    SELECT problem_text"
                    "    FROM PROBLEM"
                    "    WHERE"
                    "        PROBLEM.problem_id = GAME_INFO.problem_id"
                    ") as problem_text "
                    "FROM GAME_INFO "
                    "WHERE   game_id=%s ",
                    (game_id)
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

       