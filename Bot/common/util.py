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

def split_chracter(string):
    response = ""
    for char in string:
        if korean.hangul.is_hangul(char):
            response += ''.join(korean.hangul.split_char(char))
        else:
            response += char
    return response

def get_edit_distance(string1, string2):

    s1 = split_chracter(string1)
    s2 = split_chracter(string2)

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
    return ((len(s) - distance) / len(s)) * 100

def get_speed (s, time):
    return len(s) / ((time/1000)*60)

def generate_game_id ():
    return uuid.uuid4()
