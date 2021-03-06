# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json 
import logging 


with open('../conf.json') as conf_json:
    conf = json.load(conf_json)


# get logger
db_manager_logger = logging.getLogger('sqlalchemy.pool')

# make log format
formatter = logging.Formatter('[ %(levelname)s | %(filename)s:%(lineno)s ] %(asctime)s > %(message)s')

# set log handler
fileHandler = logging.FileHandler('./db_manager_logs.log')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()

db_manager_logger.addHandler(fileHandler)
db_manager_logger.addHandler(streamHandler)

# set log level
db_manager_logger.setLevel(logging.DEBUG)

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

# query with args
"""
def query(queryString, params = None):
    db_manager_logger.info("query : " + queryString)
    if params != None:
        params = list(params)
        db_manager_logger.info("params : " + str(params))
        for idx, arg in enumerate(params):
            db_manager_logger.info(arg)
            if isinstance(arg, bytes):
                arg = arg.decode('utf-8')
            params[idx] = "'"+str(arg)+"'"
        params = tuple(params)
        queryString = queryString % params

    result = session.execute(queryString)
    return result
"""

def query(queryString, params = None):
    db_manager_logger.info("query : " + queryString)

    i=0
    while '%s' in queryString:
        queryString = queryString.replace('%s', ':p'+str(i), 1)
        i+=1

    if params != None:
        params = list(params)
        db_manager_logger.info("params : " + str(params))
        args = {}
        for idx, arg in enumerate(params):
            key = 'p'+str(idx)
            args[key] = arg

        result = session.execute(queryString, args)
    else:
        result = session.execute(queryString)

    return result
