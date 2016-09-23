# #-*- coding: utf-8 -*-
import json
with open('conf.json') as json_data:
    data = json.load(json_data)

#기본 데이터셋
admin = data["mysql"]["admin"]
password = data["mysql"]["password"]
host = data["mysql"]["host"]
db = data["mysql"]["db"]

from sqlalchemy import create_engine
# 커낵션은 쿼리가 실행되야 연결된다.
def sqlConnection():
	engine = create_engine('mysql+pymysql://'+admin+':'+password+'@'+host+'/'+db,
                       pool_size=20, max_overflow=0,echo=True)
	return engine

#연결 확인용 로그로 남겨둔다.
print (sqlConnection().execute("select 1").scalar())

