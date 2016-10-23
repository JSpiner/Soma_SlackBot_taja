
from celery_test import worker
import time

for i in range(0,100):
    print(i)
    worker.delay(i)
#    time.sleep(1.0 / 1000.0)
 