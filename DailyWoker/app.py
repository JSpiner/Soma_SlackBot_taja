import schedule
import time


def job():
    print("working well!")

# 10분마다 
schedule.every(10).minutes.do(job)
# 매 시간마다
schedule.every().hour.do(job)
# 매일 특정 시간에
schedule.every().day.at("09:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1) 