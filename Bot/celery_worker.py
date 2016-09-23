from celery import Celery

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

@app.task
def worker(x):
    return x
