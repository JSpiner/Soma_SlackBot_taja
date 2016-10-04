from slackclient import SlackClient
from multiprocessing import Process
import json


#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

def tester_work(api_token):

    print(api_token)

    return

testerProcess1 = Process(
    target=tester_work, 
    args=(key['slackbots'][0]['api_token'])
)
testerProcess2 = Process(
    target=tester_work, 
    args=(key['slackbots'][1]['api_token'])
)
testerProcess3 = Process(
    target=tester_work, 
    args=(key['slackbots'][2]['api_token'])
)


testerProcess1.start()
testerProcess2.start()
testerProcess3.start()