
# #-*- coding: utf-8 -*-
# static variables

GAME_COMMAND_START      = ".시작"
GAME_COMMAND_RANK       = ".점수"
GAME_COMMAND_MY_RANK    = ".내점수"
GAME_COMMAND_EXIT       = ".강제종료"

# 0 = 게임이 실행중이지 않을 때
# 1 = 카운트 다운 할 때 (Ready부터 제시어가 나올 때까지)
# 2 = 게임이 실행중일 때
# 3 = 게임 종료 후 순위 계산 할 때


GAME_STATE_IDLE = "0"
GAME_STATE_STARTING = "1"
GAME_STATE_PLAYING = "2"
GAME_STATE_CALCULATING = "3"
