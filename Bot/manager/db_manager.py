# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine

import json
with open('conf.json') as conf_json:
    conf = json.load(conf_json)


# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine('mysql+pymysql://'+conf["mysql"]["user"]+':'+conf["mysql"]["password"]+'@'+conf["mysql"]["host"]+'/'+conf["mysql"]["database"]+"?charset=utf8",pool_size=20, max_overflow=10,echo=True,execution_options={"autocommit": False})




