from celery_worker import worker

worker.delay(random.randint(0,100))
