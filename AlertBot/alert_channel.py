
import sys 
sys.path.append("../")
from Common.manager import db_manager
from Common import util
from Common.slackapi import SlackApi


result = db_manager.query(
    "select * from TEAM "
)
rows = util.fetch_all_json(result)

print(rows)