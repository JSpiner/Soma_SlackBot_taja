
from celery import Celery
import time
app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

@app.task
def worker(data):
    print("start : " + str(data))
#    time.sleep(10)
#    print("end : " + str(data))

    return 0  