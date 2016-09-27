from celery import Celery
from manager import redis_manager
from common import static
from common import util

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
# 타이머 실행 함수(게임 종료시)
def game_end(data):

    # slackclient.rtm_send_message(data["channel"], "Game End")

    # 현재 상태 변경
    redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)

    start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
    game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
    user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
    problem_id = redis_manager.redis_client.get("problem_id_" + data["channel"])

    # sql = "INSERT INTO `slack_typing_game_bot`.`game_info` " \
          # "(`game_id`, `channel_id`, `team_id`, `start_time`, `end_time`, `problem_id`, `user_num`) " \
          # "VALUES (%s, %s, %s, %s, %s, %s, %s);"

    # db_manager.curs.execute(sql, (game_id, data["channel"], data["team"], start_time, time.time(), problem_id , user_num))



@app.task
def worker(data):
    if data["text"] == static.GAME_COMMAND_START:
        #방 상태는 시작 상태
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_STARTING)

        # slackclient.rtm_send_message(data["channel"], "Ready")
        i = 3
        while i !=0 :
        	#32~~!
            # slackclient.rtm_send_message(data["channel"], i)
            time.sleep(1)
            i = i-1

        #문제 보내주기
        problem_id = random.random() * 100 % (len(texts))
        problem_text = texts[problem_id]
        ##문제내는 부분
        
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_PLAYING)
        #시작 시간 설정
        redis_manager.redis_client.set("start_time_" + data["channel"], time.time())
        #해당 게임 문자열 설정
        redis_manager.redis_client.set("problem_text_" + data["channel"], problem_text)
        redis_manager.redis_client.set("problem_id_" + data["channel"], problem_id)
        #현재 게임의 ID
        redis_manager.redis_client.set("game_id_" + data["channel"], util.generate_game_id())

        # 타이머 돌리기
        threading.Timer(len(problem_text) * 2, game_end, [data]).start()


    elif data["text"] == "점수":
    	print("점수")
    	#점수디비에서 가져오기
        #해당 채널 전체 점수 보내주기
        # slackclient.rtm_send_message(data["channel"], "Result")

    elif data["내점수"] == "내점수":
        print ("내 점수:)")
        #내 점수만 나에게 Direct 메시지로 보내주기
        #direct message가 갈 수 있는지 확인...

    #채널에 접속했을떄
    elif data["type"] == "channel_joined":
    	print("channel joined")

    elif data["type"] == "team_joined":
    	print("tema joined")



    else:
        distance = util.get_edit_distance(data["text"], redis_manager.redis_client.get("problem_text_" + data["channel"]))

        speed = 0
        accuracy = 0

        start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
        current_time = time.time()
        elapsed_time = current_time - start_time

        game_id = redis_manager.redis_client.get("game_id_" + data["channel"])

        # 참여 유저수 증가
        user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
        redis_manager.redis_client.set("user_num_" + data["channel"], user_num + 1)

        # 만점
        if distance == 0 :
            speed = util.get_speed(data["text"], elapsed_time)
            accuracy = 100

        # 틀린게 있을 때
        else :
            speed = util.get_speed(data["text"], elapsed_time)
            accuracy = util.get_accuracy(data["text"], distance)

