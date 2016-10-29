# #-*- coding: utf-8 -*-
import datetime
import time
import json 
# static variables

GAME_COMMAND_START      = "/start"
GAME_COMMAND_SCORE      = "/score" 
GAME_COMMAND_RANK       = "/rank"
GAME_COMMAND_MY_SCORE   = "/myscore"
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

# socket expire time
SOCKET_EXPIRE_TIME = 30 #60*60

# current_milli_time = lambda: int(round(time.time() * 1000))
TIME_CURRENT = lambda: int(round(time.time() * 1000))

# defaultError = lambda err: {'error' : err}

# ERR_DEFAULT = lambda err: { 'code': 400, 'data' : err} 

RES_DEFAULT = lambda code,data: {'code' : code,'data' : data}
# defaultResponse = lambda code,data: {'code' : code,'data' : data}

# string data code
CODE_TEXT_GAME_START        = "code_game_start"
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
