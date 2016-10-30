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


#게임 이벤트를 뽑는다.

def pickUpGameEvent(channelId):
	print('pickUp GameEvent')
	
	#기존 레디스정보가있다면 None 로 초기화시켜라 ==> None 은 없는것이나 마찬가지
	# redis_client.set(static.GAME_MISSION_ID + channelId, None)
	redis_client.set(static.GAME_MISSION_NOTI + channelId, None)
	redis_client.set(static.GAME_MISSION_CONDI + channelId, None)

	#미션실행 모드이다. 
	#현재 테스트용으로 50% 확률로 미션게임이 나오도록 작업하였다.
	if util.getRandomValue(1,2) == 1 :
		print('mission start')
		result = db_manager.query(
			"SELECT * FROM GAME_MISSION WHERE validity = 1 ORDER BY rand() LIMIT 1 "
		)
		rows = util.fetch_all_json(result)
		mission_id = rows[0]['mission_id']
		mission_noti = rows[0]['mission_noti']
		mission_condi = rows[0]['condi'];


		# redis_client.set(static.GAME_MISSION_ID + channelId,mission_id)
		redis_client.set(static.GAME_MISSION_NOTI + channelId,mission_noti)
		redis_client.set(static.GAME_MISSION_CONDI + channelId,mission_condi)

		return static.GAME_TYPE_MISSION
	#노말 모드이다.
	else :
		print('normal')
		redis_client.set(static.GAME_MISSION_NOTI + channelId, None)
		redis_client.set(static.GAME_MISSION_CONDI + channelId, None)
		return static.GAME_TYPE_NORMAL


def is_mission_clear(channel_id,game_id):
	print('isMiission clear')
	print(channel_id)
	print(game_id)
	global arr_cond_oper 
	arr_cond_oper = []
	print(redis_client.get(static.GAME_MISSION_CONDI+channel_id))
	mission_condi = json.loads(redis_client.get(static.GAME_MISSION_CONDI+channel_id));
	print(mission_condi)
	result = db_manager.query(
		"select * from GAME_INFO as gi inner join GAME_RESULT as gr on gi.game_id = gr.game_id where  gi.game_id = %s",
		(game_id,)
	)
	rows = util.fetch_all_json(result)

	print('mission COidn ==> '+str(mission_condi));
	print('game id ==> '+game_id)
	print('rows ==> '+str(rows))
	user_num = len(rows)



	mission_success_num = 0

	#총 참여인원이 모자라라서 미션을 하지못하였다
	if(check_enter_member(mission_condi,user_num)==False):
		print('인원이 부족하여 미션을 참여 못하였습니다.')
		return static.GAME_MISSION_ABSENT
	else:
		print('인원은 충분합니다.')
		#미션조건으로부터 연산 조건을 뽑아와 arr_cond_oper에 넣는다.
		check_conditions(mission_condi)
		for oper in arr_cond_oper:
			print('added operations==> '+oper)

		for row in rows:
			chcked_user = checking_user(row,mission_condi)
			
			#미션성공시+1 을 해준다.
			if(chcked_user == True):
				mission_success_num = mission_success_num + 1

		print('mission sucess Num ===>',mission_success_num)
		
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
		print(row['user_id']+'==> 미션 성공!!')
		return True
	else:
		print(row['user_id']+'==> 미션실패!!!')
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
		print("미션을 모두 참여자가 모두 만족해야합니다.")
		if(checked_user == user_num):
			print("모든유저가 모두 성공했습니다."+str(user_num)+"명")
			return True
		else:
			print("모든유저가 성공하지 못했습니다"+str(user_num)+"명")
			return False
	else:
		if(checked_user>=nec_member):
			print(str(nec_member)+ "성공멤버 수 채웠습니다")
			return True
		else:
			print(checked_user+"/"+str(nec_member)+ "성공멤버 수 를 채우지 못했습니다")
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









	
	



