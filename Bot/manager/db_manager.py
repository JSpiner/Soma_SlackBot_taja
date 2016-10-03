# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine

import json
with open('conf.json') as conf_json:
    conf = json.load(conf_json)


# def FetchAllAssoc(cursor) :
#     desc = cursor
#     results = [dict(zip([col[0] for col in desc], row)) 
#             for row in cursor.fetchall()]
#     return results


# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine('mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"]+"?charset=utf8",pool_size=20, max_overflow=0,echo=True,execution_options={"autocommit": False})


#### DB_Connection EX_INSERT ###
# 아래와같이 trans인스턴스를 만들어주고 commit까지해야 올바르게 데이터에 값이 들어간다.
# conn = engine.connect()
# trans = conn.begin()

# conn.execute("insert into PROBLEM (problem_id,problem_text) values(%s,%s) ",0,"hellocc")
# trans.commit()
# conn.close()
# 참고:http://docs.sqlalchemy.org/en/latest/core/connections.html#understanding-autocommit


#### DB_Connection EX_Select ###(app.js에서 테스트하세요)
# conn = db_manager.engine.connect()
# result = conn.execute("select *from GAME_RESULT")
# conn.close()
# print(util.fetch_all_json(result))
## 결과.
# [{'accuracy': -225.0, 'score': -4475.38, 'elapsed_time': 3.35167, 'speed': 19.8906, 'answer_text': '????', 'game_id': '29f7845a-2cfc-438b-bd43-0fda3c7ac2cb', 'user_id': 'U23HTB8G0'}, {'accuracy': -450.0, 'score': -5933.7, 'elapsed_time': 5.05589, 'speed': 13.186, 'answer_text': 'aaaa', 'game_id': '8a727268-0c47-4aeb-8ab9-5eacf1bd2479', 'user_id': 'U23HTB2AC'}, {'accuracy': 35.714, 'score': 1602.81, 'elapsed_time': 5.19921, 'speed': 44.879, 'answer_text': '??? ??????!!!!', 'game_id': '8a727268-0c47-4aeb-8ab9-5eacf1bd2479', 'user_id': 'U23HTB8G0'}, {'accuracy': 100.0, 'score': 3823.6, 'elapsed_time': 4.7948, 'speed': 38.236, 'answer_text': '????? ?????', 'game_id': 'a00d5f0a-b965-4746-82fc-b7876afbfdc5', 'user_id': 'U23HTB2AC'}, {'accuracy': 90.0, 'score': 3689.37, 'elapsed_time': 4.06575, 'speed': 40.993, 'answer_text': '??????????', 'game_id': 'a00d5f0a-b965-4746-82fc-b7876afbfdc5', 'user_id': 'U23HTB8G0'}, {'accuracy': 66.667, 'score': 3044.95, 'elapsed_time': 3.28417, 'speed': 45.674, 'answer_text': '?????????', 'game_id': 'a5e78d12-ee0c-4a48-aa1b-deb75c9e234d', 'user_id': 'U23HTB8G0'}, {'accuracy': -28.571, 'score': -919.615, 'elapsed_time': 3.62464, 'speed': 32.187, 'answer_text': '???????', 'game_id': 'aa8213da-bfca-4407-a6ea-d5e580c6bdb4', 'user_id': 'U23HTB8G0'}, {'accuracy': -11.111, 'score': -382.585, 'elapsed_time': 4.35629, 'speed': 34.433, 'answer_text': '?????????', 'game_id': 'bb1c4a0b-b329-42f2-b0c3-bd0274652440', 'user_id': 'U23HTB8G0'}, {'accuracy': -60.0, 'score': -2023.26, 'elapsed_time': 7.4138, 'speed': 33.721, 'answer_text': '??????? ??? ???', 'game_id': 'd7c13279-23ce-4574-9201-ff656bb6901b', 'user_id': 'U23HTB8G0'}, {'accuracy': 83.333, 'score': 4007.73, 'elapsed_time': 4.15864, 'speed': 48.093, 'answer_text': '??? ??? ???!', 'game_id': 'dfac0ec5-ca1c-4f73-ac41-33cad79fad30', 'user_id': 'U23HTB8G0'}]




