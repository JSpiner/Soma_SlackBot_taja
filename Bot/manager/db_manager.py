# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json 
with open('conf.json') as conf_json:
    conf = json.load(conf_json)
 

# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine(
    'mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"]+"?charset=utf8",
    pool_size = 20, 
    pool_recycle = 500, 
    max_overflow = 10,
    echo = True,
    echo_pool = True,
    execution_options = {"autocommit": True}
)
 
session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=False,
                                         bind=engine))
#session.begin()

def query(queryString, params):
    print("query : " + queryString)
    print("params : " + str(params))
    params = list(params)
    for idx, arg in enumerate(params):
        print(arg)
        if isinstance(arg, bytes):
            arg = arg.decode('utf-8')
        params[idx] = "'"+str(arg)+"'"
    params = tuple(params)

    queryString = queryString % params
    result = session.execute(queryString)
#    session.commit()
    return result
