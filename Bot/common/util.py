# #-*- coding: utf-8 -*-
import uuid
import korean
import threading
from functools import wraps

# delay
def delay(delay=0.):
   def wrap(f):
       @wraps(f)
       def delayed(*args, **kwargs):
           timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
           timer.start()
       return delayed
   return wrap

def split_character(string):
    response = ""
    for char in string:
        if korean.hangul.is_hangul(char):
            response += ''.join(korean.hangul.split_char(char))
        else:
            response += char
    return response

def get_edit_distance(string1, string2):

    s1 = split_character(string1)
    s2 = split_character(string2)

    d = [[0 for col in range(len(s2) + 1)] for row in range(len(s1) + 1)]

    for i in range(0, len(s1) + 1):
        d[i][0] = i

    for i in range(0, len(s2) + 1):
        d[0][i] = i

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min([d[i - 1][j - 1] + 1, d[i][j - 1] + 1, d[i - 1][j] + 1])

    return d[len(s1)][len(s2)]

def get_accuracy (s, distance):
    l = len(split_character(s))
    return ((l - distance) / l)

def get_speed (s, time):
    l = len(split_character(s))
    return l / (time/1000)*60

#accur : 0.0 ~ 1.0
#speed : 0.0 ~ 400(or more)
#score : 0.0 ~ 400(or more)
def get_score(speed, accur):
    conv_accur = pow(accur, 2)
    score = conv_accur * speed

    return score


def generate_game_id ():
    return uuid.uuid4()


def fetch_all_json(result):
  lis = []

  for row in result.fetchall():
    i =0
    dic = {}  
    
    for data in row:
      # if(len(result.keys())
      # print(len(result.keys()))
      # print(i)
      # print(data)
      dic[result.keys()[i]]= data
      if i == len(row)-1:
        lis.append(dic)

      i=i+1
  return lis