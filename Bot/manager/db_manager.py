# #-*- coding: utf-8 -*-

import pymysql
import json
with open('conf.json') as conf_json:
    conf = json.load(conf_json)

    ##안되서 임시로 
conn = pymysql.connect(host='localhost', user='root', password='1234!',
                       db='taja', charset='utf8')
curs = conn.cursor()


# MySQL Connection 연결
# conn = pymysql.connect(
#     conf["mysql"]["host"],
#     port=3306,
#     conf["mysql"]["user"],
#     conf["mysql"]["password"],
#     conf["mysql"]["db"],
#     'utf8')

# conndb = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="urungses", db="SMBand")




# Connection 으로부터 Cursor 생성


# # SQL문 실행
# sql = "select * from customer"
# curs.execute(sql)

# # 데이타 Fetch
# rows = curs.fetchall()
# print(rows)  # 전체 rows
# # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
# # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')

# # Connection 닫기
# conn.close()


# slack 평강이형 코드 참고
# https://namtang.slack.com/files/twpower/F2FKBHLJC/-.py
