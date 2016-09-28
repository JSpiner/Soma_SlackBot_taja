# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine
import json
with open('conf.json') as conf_json:
    conf = json.load(conf_json)

# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine('mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"],pool_size=20, max_overflow=0,echo=True,execution_options={"autocommit": False})


#### DB_Connection EX ###
# 아래와같이 trans인스턴스를 만들어주고 commit까지해야 올바르게 데이터에 값이 들어간다.
# conn = engine.connect()
# trans = conn.begin()

# conn.execute("insert into PROBLEM (problem_id,problem_text) values(%s,%s) ",0,"hellocc")

# trans.commit()
# conn.close()
# 참고:http://docs.sqlalchemy.org/en/latest/core/connections.html#understanding-autocommit

