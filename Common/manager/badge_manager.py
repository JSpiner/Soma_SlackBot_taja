from Common.slackapi import SlackApi
from Common.manager.redis_manager import redis_client
from Common.manager import db_manager
from Common import util
from Common import static
import json
import logging
import time
from celery.utils.log import get_task_logger

def calc_badge(data):
    
    """
    팀 뱃지

    * 0 : '입문자' : 10판 플레이
    1 : '세계정복' : 모든 채널에 봇이 초대됨
    * 2 : '동작그만' : 게임취소 명령어를 1회 사용
    * 3 : '게임중독' : 200판 플레이
    4 : '만장일치' : 팀 내 모든 플레이어가 1회이상 게임 참여
    
    
    개인 뱃지

    0 : 'POTG' : 1등을 연속으로 3번 했을때
    1 : '동반입대' : 특정플레이어와 2명이서 10판 이상 플레이
    2 : '저승사자' : 연속 5번 1위
    3 : '콩진호' : 22번 연속 2위
    4 : '도와줘요 스피드웨건' : /help 명령어 1회 사용
    """

    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    badgeRows = util.fetch_all_json(db_manager.query(
        "SELECT * "
        "FROM TEAM_BADGE "
        "WHERE "
        "team_id = %s ",
        (
            teamId,
        )
    ))

    if check_badge_exist(badgeRows, 0) == False:
        rows = util.fetch_all_json(db_manager.query(
            "SELECT COUNT(game_id) as game_num "
            "FROM GAME_INFO "
            "WHERE "
            "team_id = %s",
            (
                teamId,
            )
        ))
        if rows[0]['game_num'] >= 10:
            reward_badge(data, 0)

    if check_badge_exist(badgeRows, 2) == False:
        if data['text'] == static.GAME_COMMAND_EXIT:       
            reward_badge(data, 2)


    if check_badge_exist(badgeRows, 3) == False:
        rows = util.fetch_all_json(db_manager.query(
            "SELECT COUNT(game_id) as game_num "
            "FROM GAME_INFO "
            "WHERE "
            "team_id = %s",
            (
                teamId,
            )
        ))
        if rows[0]['game_num'] >= 200:
            reward_badge(data, 3)


    return 0

def check_badge_exist(rows, badge_id):

    for row in rows:
        if row['badge_id'] == badge_id:
            return True

    return False

def reward_badge(data, badgeId):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    db_manager.query(
        "INSERT INTO TEAM_BADGE "
        "(`team_id`, `badge_id`) "
        "VALUES "
        "(%s, %s)",
        (
            teamId,
            badgeId
        )
    )

    time.sleep(1)
    slackApi.chat.postMessage(
        {
            'channel' : channelId,
            'text' : static.getText(static.CODE_TEXT_NEW_BADGE, teamLang),
            'attachments'   : json.dumps(
                [
                    {
                        "text": static.getText(static.CODE_TEXT_TEAM_BADGES[badgeId], teamLang),
                        "fallback": "fallbacktext",
                        "callback_id": "wopr_game",
                        "color": "#3AA3E3",
                        "attachment_type": "default"
                    }
                ]
            )
        }
    )

    if badgeId == 0:
        time.sleep(3)
        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text' : static.getText(static.CODE_TEXT_GAME_REVIEW, teamLang)
            }
        )

    return 0