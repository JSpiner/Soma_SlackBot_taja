# #-*- coding: utf-8 -*-
import datetime
import time
import json 
# static variables

GAME_COMMAND_START      = "/start"
GAME_COMMAND_SCORE      = "/score" 
GAME_COMMAND_RANK       = "/rank"
GAME_COMMAND_KOK        = "/kok"
GAME_COMMAND_MY_SCORE   = "/myscore"
GAME_COMMAND_BADGE      = "/badge"
GAME_COMMAND_EXIT       = "/exit"

# 0 = 게임이 실행중이지 않을 때
# 1 = 게임 시작 요청 수립 후 소켓연결대기상태 
# 2 = 카운트 다운 할 때 (Ready부터 제시어가 나올 때까지)
# 3 = 게임이 실행중일 때
# 4 = 게임 종료 후 순위 계산 할 때


GAME_STATE_IDLE         = "0"
GAME_STATE_LOADING      = "1"
GAME_STATE_STARTING     = "2"
GAME_STATE_PLAYING      = "3"
GAME_STATE_CALCULATING  = "4"

# rtm socket status
SOCKET_STATUS_IDLE          = "0"
SOCKET_STATUS_CONNECTING    = "1"
SOCKET_STATUS_CONNECTED     = "2"
SOCKET_STATUS_RECONNECTING  = "3"

# copy&paste check string
CHAR_PASTE_ESCAPE = " " # HAIR SPACE

#후에 다양해질 게임에 대하여 게임타입을 추가해 준다.
GAME_TYPE_NORMAL = "GAME_TYPE_NORMAL"
GAME_TYPE_MISSION = "GAME_TYPE_MISSION"

#게임미션 아이디를 Redis에서 관리할것이다(채널별로)
GAME_MISSION_NOTI_CODE = "GAME_MISSION_NOTI_CODE_"
GAME_MISSION_NOTI= "GAME_MISSION_NOTI_"
GAME_MISSION_CONDI= "GAME_MISSION_CONDI_"
GAME_MISSION_TYPE= "GAME_MISSION_TYPE_"


#게임미션 엔드
GAME_MISSION_FAILE = "MISSION FAILE!!!!!!"
GAME_MISSION_SUC = "MISSION SUCCESS!!!!!"
GAME_MISSION_ABSENT = "MISSION ABSENT!!!!!!"

#미션게임 코드
GAME_MISSION_REVERSE = 101

# socket expire time
SOCKET_EXPIRE_TIME = 60*60

# current_milli_time = lambda: int(round(time.time() * 1000))
TIME_CURRENT = lambda: int(round(time.time() * 1000))

# defaultError = lambda err: {'error' : err}

# ERR_DEFAULT = lambda err: { 'code': 400, 'data' : err} 

RES_DEFAULT = lambda code,data: {'code' : code,'data' : data}
# defaultResponse = lambda code,data: {'code' : code,'data' : data}

# string data code
CODE_TEXT_LANG_CHANGED      = "code_lang_changed"
CODE_TEXT_JOIN_BOT          = "code_join_bot"
CODE_TEXT_ALREADY_STARTED   = "code_already_started"
CODE_TEXT_BUTTON_LANG       = "code_button_lang"
CODE_TEXT_BOT_NOTFOUND      = "code_bot_notfound"
CODE_TEXT_INVITE_BOT        = "code_invite_bot"
CODE_TEXT_INVITE            = "code_invite"
CODE_TEXT_INVITE_ASK        = "code_invite_ask"
CODE_TEXT_CAN_REMOVE        = "code_can_remove"
CODE_TEXT_OPTION_INVITE     = "code_option_invite"
CODE_TEXT_OPTION_LATER      = "code_option_later"
CODE_TEXT_START_GAME        = "code_start_game"
CODE_TEXT_COUNT_1           = "code_count_1"
CODE_TEXT_COUNT_2           = "code_count_2"
CODE_TEXT_COUNT_3           = "code_count_3"
CODE_TEXT_SUGGEST_PROBLEM   = "code_suggest_problem"
CODE_TEXT_START_GAME_COUNT  = "code_start_game_count"
CODE_TEXT_START_GAME_END    = "code_start_game_end"
CODE_TEXT_GAME_DONE         = "code_game_done"
CODE_TEXT_RANK_FORMAT_1     = "code_rank_format_1"
CODE_TEXT_RANK_FORMAT_2     = "code_rank_format_2"
CODE_TEXT_RANK_FORMAT_3     = "code_rank_format_3"
CODE_TEXT_RANK_FORMAT_4     = "code_rank_format_4"
CODE_TEXT_MY_SCORE          = "code_my_score"
CODE_TEXT_RECORD            = "code_record"
CODE_TEXT_SCORE             = "code_score"
CODE_TEXT_RANK              = "code_rank"
CODE_TEXT_WARNING_PASTE     = "code_warning_paste"
CODE_TEXT_CALC_SCORE        = "code_calc_score"
CODE_TEXT_GAME_RESULT       = "code_game_result"
CODE_TEXT_CHOOSE_LANG       = "code_choose_lang"
CODE_TEXT_KOK_TITLE         = "code_kok_title"
CODE_TEXT_KOK_ENTRY         = "code_kok_entry"
CODE_TEXT_KOK_ROUND         = "code_kok_round"
CODE_TEXT_GAME_REVIEW       = "code_game_review"
CODE_TEXT_NEW_BADGE         = "code_new_badge"


CODE_TEXT_TEAM_BADGES = [
    "code_team_badge_1",
    "code_team_badge_2",
    "code_team_badge_3",
    "code_team_badge_4",
    "code_team_badge_5"
]

#for mission
CODE_TEXT_MISSION_RESULT_MIN_MEMBER      	 = "code_text_mission_result_min_member"
CODE_TEXT_MISSION_RESULT_SUCCESS       		 = "code_text_mission_result_success"
CODE_TEXT_MISSION_RESULT_FAIL    	  	     = "code_text_mission_result_fail"



# load json lang file
with open('../Common/lang.json', 'r') as f:
    lang = json.load(f)

def getText(textCode, langCode):
    print(langCode)
    if langCode == "kr":
        return lang['kr'][textCode]
    elif langCode == "en":
        return lang['en'][textCode]
    else :
        return lang['en'][textCode]
