from slackclient import SlackClient
from multiprocessing import Process
import json


#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

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
                    print(2)
                    game_status = 2
                    game_bot_id = data['bot_id']
                    continue
                if ('bot_id' in data) is False:
                    continue	
                if data['bot_id'] == game_bot_id and data['text'] == '1':
                    print(3)
                    game_status = 3
                    continue
                if data['bot_id'] == game_bot_id and game_status == 3:

                    print(4)
                    sc.rtm_send_message(data['channel'], 'hi' + str(processId))
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