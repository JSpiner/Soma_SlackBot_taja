import schedule
import time
# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine

import sys 
sys.path.append("../")


import json
with open('../conf.json') as conf_json:
    conf = json.load(conf_json)

# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine('mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"]+"?charset=utf8",pool_size=20, max_overflow=0,echo=True,execution_options={"autocommit": False})


def fetch_all_json(result):
    lis = []

    for row in result.fetchall():
	    i =0
	    dic = {}  
	    
	    for data in row:
	      # if(len(result.keys())
	      # print(len(result.keys()))
	      # print(i)
	      # print(data)
	        dic[result.keys()[i]]= str(data)
	        if i == len(row)-1:
	            lis.append(dic)

	        i=i+1
    return lis   

def updateUserActive():
	print('udate')

	# active 유저로만들기!
	try:
		conn = engine.connect()

		trans = conn.begin()
		result = conn.execute(
			"select * from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime > DATE_SUB(CURDATE() , INTERVAL 7 DAY)"
		)
		rows= fetch_all_json(result)

		arrQueryString=[]
		arrQueryString.append('update USER set USER.isActive = 1 where ')

		for row in rows:
			arrQueryString.append('USER.user_id = "'+ row['user_id']+ '"')
			arrQueryString.append(' or ')

		arrQueryString.pop()
		lastQuery = "".join(arrQueryString)

		
		result = conn.execute(
			lastQuery
		)

		arrQueryString=[]
		arrQueryString.append('insert into USER_DAILY_ACTIVE (date,user_id,active) values ')
		for row in rows:
			arrQueryString.append('(curdate(),"'+ row['user_id']+ '",1)')
			arrQueryString.append(',')

		arrQueryString.pop()
		lastQuery = "".join(arrQueryString)
		print(lastQuery)

		conn.execute(
			lastQuery
		)
		trans.commit()
		conn.close() 
	except Exception as e:
		print(str(e))

	try:
		conn = engine.connect()

		trans = conn.begin()
		result = conn.execute(
			"select * from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime < DATE_SUB(CURDATE() , INTERVAL 7 DAY)"
		)
		rows= fetch_all_json(result)
		print(rows)
		if len(rows)==0:
			trans.commit()
			conn.close() 
		else :				
			arrQueryString=[]
			arrQueryString.append('update USER set USER.isActive = 0 where ')

			for row in rows:
				arrQueryString.append('USER.user_id = "'+ row['user_id']+ '"')
				arrQueryString.append(' or ')

			arrQueryString.pop()
			lastQuery = "".join(arrQueryString)

			
			result = conn.execute(
				lastQuery
			)

			arrQueryString=[]
			arrQueryString.append('insert into USER_DAILY_ACTIVE (date,user_id,active) values ')
			for row in rows:
				arrQueryString.append('(curdate(),"'+ row['user_id']+ '",0)')
				arrQueryString.append(',')

			arrQueryString.pop()
			lastQuery = "".join(arrQueryString)
			print(lastQuery)

			conn.execute(
				lastQuery
			)
			trans.commit()
			conn.close() 
	except Exception as e:
		print(str(e))		


def job():
	print("working well!")
	updateUserActive()
	# updateUserActive()


# 10분마다 
# schedule.every(10).minutes.do(job)
# # 매 시간마다
# schedule.every().hour.do(job)
# 매일 특정 시간에
schedule.every().day.at("00:00").do(job)





while 1:
    schedule.run_pending()
    time.sleep(1) 