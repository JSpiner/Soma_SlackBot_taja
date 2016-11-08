#미션모드일경우. 
	#1. 디비에서 미션을 선택하고.
	#2. 레디스에서 해당 미션을 관리하여 
	#3. 마지막에 해당 미션에 알맞게 정보를 재정비하여 뿌려준다.

import sys 
sys.path.append("../../Bot")

from Common.manager.redis_manager import redis_client
from Common.manager import db_manager
from Common import util
from Common import static
import json
import logging
import korean
from celery.utils.log import get_task_logger




#게임 이벤트를 뽑는다.
# get logger
logger_celery = get_task_logger(__name__)

# make log format
formatter = logging.Formatter('[ %(levelname)s | %(filename)s:%(lineno)s ] %(asctime)s > %(message)s')

# set handler
fileHandler = logging.FileHandler('./logs/Bot_celery_worker.log')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()

logger_celery.addHandler(fileHandler)
logger_celery.addHandler(streamHandler)

# set log level
logger_celery.setLevel(logging.DEBUG)

def pickUpGameEvent(channelId,teamId):
	
	logger_celery.info('[MISSION]==>pickUp GameEvent')
	teamLang = util.get_team_lang(teamId)

	#기존 레디스정보가있다면 None 로 초기화시켜라 ==> None 은 없는것이나 마찬가지
	# redis_client.set(static.GAME_MISSION_ID + channelId, None)
	redis_client.set(static.GAME_MISSION_NOTI + channelId, 'None')
	redis_client.set(static.GAME_MISSION_CONDI + channelId, 'None')
	redis_client.set(static.GAME_MISSION_TYPE + channelId, 'None')
	redis_client.set(static.GAME_MISSION_NOTI_CODE + channelId,'None')

	#첫판일경우 100
	play_cnt = redis_client.get(static.GAME_MANAGER_PLAY_COUNTER+channelId)

	if( play_cnt == '1' or play_cnt == '2'):
		play_mission_per = 0
		play_mission_general = 'None'
		play_mission_id = 'None'
	elif(play_cnt == '3'):
		play_mission_per = 100
		play_mission_general = 0
		play_mission_id = 101
	elif(play_cnt == '4'):
		play_mission_per = 100
		play_mission_general = 0
		play_mission_id = 103
	elif(play_cnt == '5'):
		play_mission_per = 100
		play_mission_general = 0
		play_mission_id = 102
	elif(play_cnt == '6'):
		play_mission_per = 100
		play_mission_general = 100
		play_mission_id = 1
	elif(play_cnt == '7'):
		play_mission_per = 100
		play_mission_general = 100
		play_mission_id = 2							
	else:
		play_mission_per = 80
		play_mission_general = 30
		play_mission_id = 'None'


	print(' playCnt => ' +str(play_cnt)+' missionper => '+str(play_mission_per)+ ' play_general=> '+str(play_mission_general)+' play_di => '+str(play_mission_id))

	#미션실행 모드이다. 
	#현재 테스트용으로 50% 확률로 미션게임이 나오도록 작업하였다.
	if util.getRandomPercent(play_mission_per) :

		#다시 50% 확률로 general/special 한 미션이 나온다.
		if util.getRandomPercent(play_mission_general) :
			logger_celery.info('[MISSION]==> general Mission')

			if(play_cnt=='6' or play_cnt=='7'):
				result = db_manager.query(
					"select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='general'  and mission_noti_code =%s",
					(teamLang,play_mission_id)
				)
			else:
				result = db_manager.query(
					"select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='general'  ORDER BY rand() LIMIT 1 ",
					(teamLang,)
				)

			rows = util.fetch_all_json(result)
			mission_noti_code = rows[0]['mission_noti_code']
			mission_noti = rows[0]['mission_noti']
			mission_condi = rows[0]['condi'];
			mission_type = rows[0]['type'];

			redis_client.set(static.GAME_MISSION_NOTI_CODE + channelId,mission_noti_code)
			redis_client.set(static.GAME_MISSION_TYPE + channelId,mission_type)
			redis_client.set(static.GAME_MISSION_NOTI + channelId,mission_noti)
			redis_client.set(static.GAME_MISSION_CONDI + channelId,mission_condi)

		else:
			logger_celery.info('[MISSION]==> special Mission')
			
			if(play_cnt=='3' or play_cnt=='4' or play_cnt=='5'):
				result = db_manager.query(
					# "select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='special'  ORDER BY rand() LIMIT 1 ",
					"select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo   on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='special'  and mission_noti_code =%s",
					(teamLang,play_mission_id)
				)
			else:
				result = db_manager.query(
					"select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='special'  ORDER BY rand() LIMIT 1 ",
					# "select *from GAME_MISSION_NOTI as gnoti inner join GAME_MISSION_INFO as ginfo   on gnoti.id = ginfo.mission_noti_code where ginfo.validity = 1 and gnoti.lang =%s and type ='special'  and mission_noti_code =103",
					(teamLang,)
				)			

			rows = util.fetch_all_json(result)
			print(rows)
			mission_noti_code = rows[0]['mission_noti_code']
			mission_noti = rows[0]['mission_noti']
			mission_type = rows[0]['type'];
			
			redis_client.set(static.GAME_MISSION_NOTI_CODE + channelId,mission_noti_code)
			redis_client.set(static.GAME_MISSION_TYPE + channelId,mission_type)
			redis_client.set(static.GAME_MISSION_NOTI + channelId,mission_noti)
		

		return static.GAME_TYPE_MISSION
	#노말 모드이다.
	else :
		logger_celery.info('[MISSION]==>NOPE! just Normal mode')

		return static.GAME_TYPE_NORMAL

# def mission_swap_change_problem(string,preChar,afterChar):
# 	#자소분해하고
# 	#바꾼다.
# 	splitedChar = util.split_character(string)
# 	splitedChar.replace(preChar,afterChar)
# 	print(korean.hangul.join_char(splitedChar))


def mission_swap_get_Random_Chosung(string,channelId,teamLang):
	# logger_celery.info('[[ㅡ/]')

	if(teamLang=='kr'):
		splitedChars = list(string)
		list_chosung = []

		# logger_celery.info('[MISSION]==>',string)
		logger_celery.info('[MISSION_string]==> '+str(string))



		for pice in splitedChars:
			try:
				list_chosung.append(korean.hangul.get_initial(pice));
			except Exception as e:
				pass

		
		random_chosung =list_chosung[util.getRandomValue(0,len(list_chosung)-1)]
		redis_client.set(static.GAME_MISSION_SWAP_CHOSUNG+channelId,random_chosung)
		logger_celery.info('[MISSION_pre]==> ',str(random_chosung))
		return random_chosung
	else:
		splitedChars= list(string)
		
		random_chosung =splitedChars[util.getRandomValue(0,len(splitedChars)-1)]
		redis_client.set(static.GAME_MISSION_SWAP_CHOSUNG+channelId,random_chosung)
		logger_celery.info('[MISSION_pre]==> ',str(random_chosung))
		return random_chosung


def mission_swap_get_options_centence(randomChar,channelId,teamLang):
	chosung_list = ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅍ','ㅌ','ㅎ']
	alpha_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

	if(teamLang =='kr'):
		chosung_list.remove(randomChar)
		after_char = chosung_list[util.getRandomValue(0,len(chosung_list)-1)]
		redis_client.set(static.GAME_MISSION_SWAP_AFTER+channelId,after_char)

	elif(teamLang=='en'):
		alpha_list.remove(randomChar)
		after_char = alpha_list[util.getRandomValue(0,len(alpha_list)-1)]
		redis_client.set(static.GAME_MISSION_SWAP_AFTER+channelId,after_char)

	options_centencs = (
		static.getText(static.CODE_TEXT_MISSION_SWAP_OPTIONS, teamLang) %
		(
			randomChar,after_char
		
		)
	)
	logger_celery.info('[MISSION_afte]==> ',str(after_char))
	return options_centencs	



def mission_reverse_typing():
	logger_celery.info('[MISSION_MODE]===>REVERSE_TYPING')



def is_mission_clear(channel_id,game_id):
	logger_celery.info('[MISSION]==>mission clear check')
	logger_celery.info('[MISSION_channel_id]==>'+str(channel_id))
	logger_celery.info('[MISSION_game_id]==>'+str(game_id))
	
	global arr_cond_oper 
	arr_cond_oper = []
	
	mission_condi = json.loads(redis_client.get(static.GAME_MISSION_CONDI+channel_id));
	logger_celery.info('[MISSION_CONDI]==>'+str(mission_condi))
	result = db_manager.query(
		"select * from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id where  gi.game_id = %s",
		(game_id,)
	)
	rows = util.fetch_all_json(result)

	
	user_num = len(rows)
	mission_success_num = 0

	#총 참여인원이 모자라라서 미션을 하지못하였다
	if(check_enter_member(mission_condi,user_num)==False):
		
		return static.GAME_MISSION_ABSENT
	else:
		logger_celery.info('[MISSION_RESULT]==> Enough member')
		#미션조건으로부터 연산 조건을 뽑아와 arr_cond_oper에 넣는다.
		check_conditions(mission_condi)
		for oper in arr_cond_oper:
			
			logger_celery.info('[MISSION_RESULT_oper]==> '+str(oper))
		for row in rows:
			chcked_user = checking_user(row,mission_condi)
			
			#미션성공시+1 을 해준다.
			if(chcked_user == True):
				mission_success_num = mission_success_num + 1
		
		logger_celery.info('[MISSION_RESULT_success_num]==> '+str(mission_success_num))
		
		if(check_nec_member(mission_condi,mission_success_num,user_num)==True):
			return static.GAME_MISSION_SUC
		else:
			return static.GAME_MISSION_FAILE



			



def checking_user(row,mission_condi):


	oper_score = arr_cond_oper[0]
	oper_accuracy = arr_cond_oper[1]
	oper_speed = arr_cond_oper[2]
	
	condition = mission_condi['codition']	
	options = condition['value']


	#기본 모두 트루.하나라도 거짓이면 조건에 만족하지 못한것임으로 미션 실패이다.
	is_score_suc = True
	is_accur_suc = True
	is_speed_suc = True

	#SCORE!!!
	if(oper_score!='dc'):
		# (미션조건 값, 비교구문, 유저값)이 들어간다.
		is_score_suc = compare(options['score'],oper_score,row['score'])

	#accuracy!!!
	if(oper_accuracy!='dc'):
		# (미션조건 값, 비교구문, 유저값)이 들어간다.
		is_accur_suc = compare(options['accuracy'],oper_accuracy,row['accuracy'])	

	#SPEED!!!
	if(oper_speed!='dc'):
		# (미션조건 값, 비교구문, 유저값)이 들어간다.
		is_speed_suc = compare(options['speed'],oper_speed,row['speed'])	

	#여기서 해당유저가 조건에 모두 맞게 랭킹을 먹었는지를 확인한다.
	if(is_score_suc == True and is_speed_suc == True and is_accur_suc == True):
		
		logger_celery.info('[MISSION_RESULT]==> '+str(row['user_id'])+'==> missino success')
		return True
	else:
		
		logger_celery.info('[MISSION_RESULT]==> '+str(row['user_id'])+'==> missino fail')
		return False

#비교해보는 로직.
def compare(mission_val,comp,user_val):

	if(comp == 'upper'):
		if(user_val>mission_val):
			return True
		else:
			return False

	elif(comp == 'same'):
		if(user_val==mission_val):
			return True		
		else:
			return False	

	elif(comp == 'lower'):
		if(user_val<mission_val):
			return True
		else:
			return False

#어떤 조건인지 일단 받아온다.
def check_conditions(mission_condi):

	condition = mission_condi['codition']	
	
	options = condition['options']

	score_opt = options['score_opt']	
	accuracy_opt = options['accuracy_opt']
	speed_opt = options['speed_opt']

	arr_cond_oper.append(score_opt)
	arr_cond_oper.append(accuracy_opt)
	arr_cond_oper.append(speed_opt)


#조건을 만족하는 사람의수.
#최종 조건이된다. 그리고 이 조건은 모두/ 일경우혹은 nec_member보다 크거나 같을경우에만 성립되도록 해놓느다(임시)
def check_nec_member(mission_condi,checked_user,user_num):
	condition = mission_condi['codition']	
	
	options = condition['options']
	nec_member = options['nec_member']

	if(nec_member == "all"):
		# print("미션을 모두 참여자가 모두 만족해야합니다.")
		logger_celery.info('[MISSION_RESULT]==> '+'all member necc')
		if(checked_user == user_num):			
			logger_celery.info('[MISSION_RESULT]==> all Member sucess '+str(user_num)+"명");
			return True
		else:			
			logger_celery.info('[MISSION_RESULT]==> all Member faile'+str(user_num)+"명");
			return False
	else:
		if(checked_user>=nec_member):
			logger_celery.info('[MISSION_RESULT]==> necc Member success'+str(user_num)+"/"+str(nec_member));			
			return True
		else:
			logger_celery.info('[MISSION_RESULT]==> necc Member fail'+str(user_num)+"/"+str(nec_member));
			return False

# [2016-10-30 02:08:54,187: WARNING/Worker-5] mission COidn ==> {'enter_members': 2, 'enter_members_opt': 'upper', 'codition': {'options': {'speed_opt': 'dc', 'nec_member': 'all', 'accuracy_opt': 'same', 'score_opt': 'dc'}, 'value': {'accuracy': 100}}, 'mission_id': 1}
#0 d이것먼저로 확인. 멤버수대로 할수있느가.
def check_enter_member(mission_condi,user_num):
	 
	enter_members = mission_condi['enter_members']
	enter_members_opt = mission_condi['enter_members_opt']
	

	#유저넘이 참여자보다 많다
	if(enter_members_opt == 'upper' and user_num>enter_members):
		return True
	
	elif(enter_members_opt == 'upper' and user_num<enter_members):
		return False

	elif(enter_members_opt == 'lower' and user_num<enter_members):
		return True

	elif(enter_members_opt == 'lower' and user_num>enter_members):
		return False

	elif(enter_members_opt == 'same' and user_num==enter_members):
		return True
	elif(enter_members_opt == 'same' and user_num!=enter_members):
		return False









	
	



