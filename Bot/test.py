
from slackclient import SlackClient
import websocket
#from slackclient import SlackNotConnected

sc = SlackClient('xoxb-91817198689-6Ps1Hv9vgp2qn5agD06nkuRB')


if sc.rtm_connect():
    print("connected! : ")

    while True:
        
        try:
            response = sc.rtm_read()
        except websocket.WebSocketConnectionClosedException as e:
            break
        except Exception as e:
            print(e)
            print(type(e))
            if str(e) == "Connection is already closed.":
                break
            if str(type(e)) == "websocket._exceptions.WebSocketConnectionClosedException":
                break
            if type(e) == "websocket._exceptions.WebSocketConnectionClosedException":
                break
            raise Exception


        if len(response) == 0:  
            continue

        # response는 배열로, 여러개가 담겨올수 있음
        for data in response:
            print(data)
print("disconnected")