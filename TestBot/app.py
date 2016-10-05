from slackclient import SlackClient
from multiprocessing import Process
import json
import random
import time

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

def rand_mix_string(str):
    str = str.replace('*', '')
    print('origin : ' + str)
    type = random.randint(1,7)
    if type==1:
        str = ''.join(random.sample(str, len(str)))
    elif type==2:
        count = random.randint(0, len(str))
        for i in range(0, count):
            pos = random.randint(1, len(str)-1 )
            str = str[:pos] + str[pos+1:]
    elif type==3:
        str = str + str
    elif type==4:
        str = str + '!'
    print('change : ' + str)
    return str

def tester_work(processId, api_token):
    print("process : " + str(processId) + " run with : " + api_token)

    game_status = 0
    game_bot_id = ""

    sc = SlackClient(api_token)
    if sc.rtm_connect():
        while True:
            response = sc.rtm_read()

            if len(response) == 0: 
                continue

            # response는 배열로, 여러개가 담겨올수 있음
            for data in response:
                print(data)

                if ('type' in data) is False:
                    continue	

                if ('text' in data) is False:
                    continue	
                
                if data['text'] == ".시작":
                    print(1)
                    game_status = 1
                    continue
                if data['text'] == "Ready~" and game_status == 1:
                    game_status = 2
                    game_bot_id = data['bot_id']
                    continue
                if ('bot_id' in data) is False:
                    continue	
                if data['bot_id'] == game_bot_id and data['text'] == '1':
                    game_status = 3
                    continue
                if data['bot_id'] == game_bot_id and game_status == 3:
                    time.sleep(random.randint(1,8))
                    sc.rtm_send_message(data['channel'], rand_mix_string(data['text']))
                    game_status = 1

 
    return

testerProcess1 = Process(
    target=tester_work, 
    args=(1, key['slackbots'][0]['api_token'])
)
testerProcess2 = Process(
    target=tester_work, 
    args=(2, key['slackbots'][1]['api_token'])
)
testerProcess3 = Process(
    target=tester_work, 
    args=(3, key['slackbots'][2]['api_token'])
)


testerProcess1.start()
testerProcess2.start()
testerProcess3.start()