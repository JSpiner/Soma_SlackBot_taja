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
                    "select count(*) as todayPlay  from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id  WHERE DATE(gi.start_time) = CURDATE() "
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

        elif types == "getActiveGraph":            
            who =  request.args.get('who')           
            period = request.args.get('period')

            if who == "user":
                if period == "day":
                    try:
                        print("[DashBoard]_GET_ActiveUserDay")
                        conn = db_manager.engine.connect()
                        getActiveUserDay = conn.execute(
                            "select hour(gi.end_time) as hour ,count(*) as cnt from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id  where gi.end_time > curdate() group by hour(gi.end_time)"
                        )
                        conn.close()
                        row_getActiveUserDay = util.fetch_all_json(getActiveUserDay)                
                                            
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveUserDay),sort_keys=True, indent = 4)

                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                


                elif period == "month":
                    try:
                        print("[DashBoard]_GET_ActiveUserMonth")

                        conn = db_manager.engine.connect()
                        getActiveUserMonth = conn.execute(
                            "select day(gi.end_time) as day ,count(*) as cnt from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id  where gi.end_time > date_sub(now(),INTERVAL 1 month)  group by day(gi.end_time)"
                        )
                        conn.close()
                        row_getActiveUserMonth = util.fetch_all_json(getActiveUserMonth)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveUserMonth),sort_keys=True, indent = 4)
                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                

                elif period == "year":
                    try:
                        print("[DashBoard]_GET_ActiveUserYear")

                        conn = db_manager.engine.connect()
                        getActiveUserYear = conn.execute(
                            "select month(gi.end_time) as month ,count(*) as cnt from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id  where gi.end_time > date_sub(now(),INTERVAL 1 year)  group by month(gi.end_time) "
                        )
                        conn.close()
                        row_getActiveUserYear = util.fetch_all_json(getActiveUserYear)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveUserYear),sort_keys=True, indent = 4)

                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                


            elif who=="team":
                
                if period == "day":                
                    try:
                        print("[DashBoard]_GET_ActiveTeamDay")
                        conn = db_manager.engine.connect()
                        getActiveTeamDay = conn.execute(
                            "select hour(gi.end_time)as hour ,count(*) as cnt from GAME_INFO as gi where gi.end_time > curdate() group by hour(gi.end_time)"
                        )
                        conn.close()
                        row_getActiveteamDay = util.fetch_all_json(getActiveTeamDay)                
                                            
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveteamDay),sort_keys=True, indent = 4)

                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                


                elif period == "month":

                    try:
                        print("[DashBoard]_GET_ActiveTeamMonth")

                        conn = db_manager.engine.connect()
                        getActiveTeamMonth = conn.execute(
                            "select day(gi.end_time)as day,count(*) as cnt from GAME_INFO as gi where gi.end_time > date_sub(now(),INTERVAL 1 month)  group by day(gi.end_time)"
                        )
                        conn.close()
                        row_getActiveTeamMonth = util.fetch_all_json(getActiveTeamMonth)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveTeamMonth),sort_keys=True, indent = 4)
                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                

                elif period == "year":
                    try:
                        print("[DashBoard]_GET_ActiveTeamYear")

                        conn = db_manager.engine.connect()
                        getActiveTeamYear = conn.execute(
                            "select month(gi.end_time)as month,count(*) as cnt from GAME_INFO as gi where gi.end_time > date_sub(now(),INTERVAL 1 year)  group by month(gi.end_time)"
                        )
                        conn.close()
                        row_getActiveTeamYear = util.fetch_all_json(getActiveTeamYear)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveTeamYear),sort_keys=True, indent = 4)

                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                                
                        
        elif types == "getTopTwenty":

            try:
                print('gettop')
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "select pb.problem_text,ga.answer_text, ga.score,ga.speed,ga.accuracy,ga.elapsed_time,u.user_name from GAME_RESULT as ga inner join USER as u on u.user_id = ga.user_id  inner join GAME_INFO as gr on gr.game_id = ga.game_id  inner join PROBLEM as pb on gr.problem_id = pb.problem_id order by score desc limit 20"
                )
                conn.close()
                rows = util.fetch_all_json(result)
                return json.dumps(static.RES_DEFAULT(200, rows), sort_keys=True, indent=4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400, "err"), sort_keys=True, indent=4)

        elif types == "getInActiveGraph":            
            who =  request.args.get('who')           
            period = request.args.get('period')
            print('getInactive')

            if who == "user":

                if period == "month":
                    try:
                        print("[DashBoard]_GET_InActiveUserMonth")

                        conn = db_manager.engine.connect()
                        getActiveUserMonth = conn.execute(
                            "select day(date) as day ,count(*) as cnt from USER_DAILY_ACTIVE where date > date_sub(now(),INTERVAL 1 month) and active = 0  group by day(date) "
                        )
                        conn.close()
                        row_getActiveUserMonth = util.fetch_all_json(getActiveUserMonth)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveUserMonth),sort_keys=True, indent = 4)
                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                

                elif period == "year":
                    try:
                        print("[DashBoard]_GET_InActiveUserYear")

                        conn = db_manager.engine.connect()
                        getActiveUserYear = conn.execute(
                            "select month(date) as month ,count(*) as cnt from USER_DAILY_ACTIVE   where date > date_sub(now(),INTERVAL 1 year)  group by month(date) "
                        )
                        conn.close()
                        row_getActiveUserYear = util.fetch_all_json(getActiveUserYear)                
                                        
                        return json.dumps(static.RES_DEFAULT(200,row_getActiveUserYear),sort_keys=True, indent = 4)

                    except Exception as e:
                        print(str(e))
                        # logging.warning(str(e))
                        return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                

            # team일떄는 후에 구현한다.
            # elif who=="team":
                
                # if period == "day":                
                #     try:
                #         print("[DashBoard]_GET_InActiveTeamDay")
                #         conn = db_manager.engine.connect()
                #         getActiveTeamDay = conn.execute(
                #             "select hour(gi.end_time)as hour ,count(*) as cnt from GAME_INFO as gi where gi.end_time > curdate() group by hour(gi.end_time)"
                #         )
                #         conn.close()
                #         row_getActiveteamDay = util.fetch_all_json(getActiveTeamDay)                
                                            
                #         return json.dumps(static.RES_DEFAULT(200,row_getActiveteamDay),sort_keys=True, indent = 4)

                #     except Exception as e:
                #         print(str(e))
                #         # logging.warning(str(e))
                #         return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                


                # elif period == "month":

                #     try:
                #         print("[DashBoard]_GET_InActiveTeamMonth")

                #         conn = db_manager.engine.connect()
                #         getActiveTeamMonth = conn.execute(
                #             "select day(gi.end_time)as day,count(*) as cnt from GAME_INFO as gi where gi.end_time > date_sub(now(),INTERVAL 1 month)  group by day(gi.end_time)"
                #         )
                #         conn.close()
                #         row_getActiveTeamMonth = util.fetch_all_json(getActiveTeamMonth)                
                                        
                #         return json.dumps(static.RES_DEFAULT(200,row_getActiveTeamMonth),sort_keys=True, indent = 4)
                #     except Exception as e:
                #         print(str(e))
                #         # logging.warning(str(e))
                #         return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                

                # elif period == "year":
                #     try:
                #         print("[DashBoard]_GET_InActiveTeamYear")

                #         conn = db_manager.engine.connect()
                #         getActiveTeamYear = conn.execute(
                #             "select month(gi.end_time)as month,count(*) as cnt from GAME_INFO as gi where gi.end_time > date_sub(now(),INTERVAL 1 year)  group by month(gi.end_time)"
                #         )
                #         conn.close()
                #         row_getActiveTeamYear = util.fetch_all_json(getActiveTeamYear)                
                                        
                #         return json.dumps(static.RES_DEFAULT(200,row_getActiveTeamYear),sort_keys=True, indent = 4)

                #     except Exception as e:
                #         print(str(e))
                #         # logging.warning(str(e))
                #         return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)                                

        
    def post(self,types):
        print("post")
        # hashKey = request.form['hashKey']                

       