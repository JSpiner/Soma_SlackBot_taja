
import sys 
sys.path.append("../")
from Common.manager import db_manager
from Common import util

db_manager.query(
    "INSERT INTO TEAM " 
    "(`team_id`, `team_name`, `team_joined_time`, `team_access_token`, `team_bot_access_token`, `bot_id`)"
    "VALUES"
    "(%s, %s, %s, %s, %s, %s)",
    ( 
        "ff",
        "ff`3!@#$%^안녕하세요 dfdfdf",
        "2016-01-01",
        "fdfdf",
        "ffff",
        "fff"
    )
)

"""
result = db_manager.session.execute(
    "SELECT * FROM TEAM WHERE team_id = :t1",
    {"t1":"1 or '1'='1'"}
)
rows = util.fetch_all_json(result)
print(rows)

db_manager.session.execute(
    "INSERT INTO TEAM " 
    "(`team_id`, `team_name`, `team_joined_time`, `team_access_token`, `team_bot_access_token`, `bot_id`)"
    "VALUES"
    "(:v1, :v2, :v3, :v4, :v5, :v6)",
    { 
        "v1":"ddd3",
        "v2":"ddd, 34` !@#$%^&* '2' \"435",
        "v3":"2016-01-01",
        "v4":"ddd",
        "v5":"ddd",
        "v6":"ddd"
    }
)

result = db_manager.session.execute(
    "SELECT * FROM TEAM WHERE team_id = 1 or '1'='1'"
)
rows = util.fetch_all_json(result)
print(rows)
"""