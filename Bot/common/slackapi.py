import requests
import sys 

SLACK_API_SERVER = "https://slack.com/api/"

class SlackApi:

    
    def __init__(self, token):
        self.token = token 
        self.__generate_apis()

    class __Api:
        def __init__(self, slackApi):
            self.slackApi = slackApi

        def test(self, args = {}):
            return self.slackApi._api_call(self, args)

    class __Auth:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def revoke(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def test(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Bots:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Channels:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def archive(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def create(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def history(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def invite(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def join(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def kick(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def leave(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def mark(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def rename(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setPurpose(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setTopic(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def unarchive(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Chat:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def delete(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def meMessage(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def postMessage(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def update(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Dnd:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def endDnd(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def endSnooze(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setSnooze(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def teamInfo(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Emoji:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Files:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def delete(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def revokePublicURL(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def sharedPublicURL(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def upload(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __Groups:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def archive(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def close(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def create(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def createChild(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def history(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def invite(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def kick(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def leave(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def mark(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def open(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def rename(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setPurpose(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setTopic(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def unarchive(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __IM:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def close(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def history(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def mark(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def open(self, args= {}):
            return self.slackApi._api_call(self, args)

    class __MPIM:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def close(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def history(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def mark(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def open(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __OAuth:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def access(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Pins:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def add(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def remove(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Reactions:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def add(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def get(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def remove(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Reminders:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def add(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def complete(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def delete(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __RTM:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def start(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Search:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def all(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def files(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def messages(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Stars:
        def __init__(self, slackApi):
            self.slackApi = slackApi
        
        def add(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def remove(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Team:
        class __Profile:
            def get(self, args= {}):
                class_name = type(self).__name__.lower()
                method_name = sys._getframe().f_code.co_name
                return slackApi.api_call(class_name+"."+method_name, args)

        def __init__(self, slackApi):
            self.slackApi = slackApi
#            profile = __Profile()
        
        def accessLogs(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def billableInfo(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def integrationLogs(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __UserGroups:
        class __Users:
            def list(self, args= {}):
                class_name = type(self).__name__.lower()
                method_name = sys._getframe().f_code.co_name
                return slackApi.api_call(class_name+"."+method_name, args)

            def update(self, args= {}):
                class_name = type(self).__name__.lower()
                method_name = sys._getframe().f_code.co_name
                return slackApi.api_call(class_name+"."+method_name, args)

        def __init__(self, slackApi):
            self.slackApi = slackApi
#            self.users = SlackApi.__UserGroups.__Users()
        
        def create(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def disable(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def enable(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def update(self, args= {}):
            return self.slackApi._api_call(self, args)
        
    class __Users:
        class __Profile:
            def get(self, args= {}):
                class_name = type(self).__name__.lower()
                method_name = sys._getframe().f_code.co_name
                return slackApi.api_call(class_name+"."+method_name, args)

            def set(self, args= {}):
                class_name = type(self).__name__.lower()
                method_name = sys._getframe().f_code.co_name
                return slackApi.api_call(class_name+"."+method_name, args)

        def __init__(self, slackApi):
            self.slackApi = slackApi
#            self.profile = SlackApi.__Users.__Profile()
        
        def deletePhoto(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def getPresence(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def identify(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def info(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def list(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setActive(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setPhoto(self, args= {}):
            return self.slackApi._api_call(self, args)
        
        def setPresence(self, args= {}):
            return self.slackApi._api_call(self, args)


    # generate api class 
    def __generate_apis(self):
        self.api = SlackApi.__Api(self)
        self.auth = SlackApi.__Auth(self)
        self.bots = SlackApi.__Bots(self)
        self.channels = SlackApi.__Channels(self)
        self.chat = SlackApi.__Chat(self)
        self.dnd = SlackApi.__Dnd(self)
        self.emoji = SlackApi.__Emoji(self)
        self.files = SlackApi.__Files(self)
        self.groups = SlackApi.__Groups(self)
        self.im = SlackApi.__IM(self)
        self.mpim = SlackApi.__MPIM(self)
        self.oauth = SlackApi.__OAuth(self)
        self.pins = SlackApi.__Pins(self)
        self.reactions = SlackApi.__Reactions(self)
        self.reminders = SlackApi.__Reminders(self)
        self.rtm = SlackApi.__RTM(self)
        self.stars = SlackApi.__Stars(self)
        self.team = SlackApi.__Team(self)
        self.usergroups = SlackApi.__UserGroups(self)
        self.users = SlackApi.__Users(self)

    # object    = api call class's instance  
    # args      = dict 
    # response  = json object
    def _api_call(self, object, args):
        class_name = type(object).__name__.lower()
        method_name = sys._getframe(1).f_code.co_name
        return self.api_call(class_name+"."+method_name, args)

    # method    = enum 
    # args      = dict 
    # response  = json object
    def api_call(self, method, args = {}):
        method = method.replace('_','')
        print(SLACK_API_SERVER + method)

        args['token'] = self.token

        r = requests.post(
            SLACK_API_SERVER + method, 
            data = args
        )
        return r.json()
        

##################################
# SlackApi Wrapper TEST CODE     #
##################################
"""
Usage

slackApi = SlackApi('API-KEY')

# call without wrapper
slackApi.api_call('chat.postMessage', args)

# call with wrapper 
slackApi.chat.postMessage(args)


"""

def testSendMessageUsingWrapper():
    result = slackApi.chat.postMessage(
        {
            'channel'   : 'C23J21PL7',
            'text'      : 'api test from python wrapper',
            'as_user'   : 'false'
        }
    )

    print(result)

def testSendMessageUsingApiCall():
    result = slackApi.api_call(
        "chat.postMessage",
        {
            "channel":"C23J21PL7","text":"api call test from PYTHON", 
            "as_user":"false"
        }
    ) 
    print(result)

def testApiTestUsingWrapper():
    result = slackApi.api.test()
    print(result)

def test():

    testApiTestUsingWrapper()
    testSendMessageUsingApiCall()
    testSendMessageUsingWrapper()
