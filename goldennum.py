# import threading
from threading import Event
from threading import Thread

import sys
# import os
import json

import requests

url = "http://127.0.0.1:8001/goldennum"
closeUser = ""
farUser = ""
userNum = 0
listUser = []
goldNum = 0
secretKey = sys.argv[1]
roomid = sys.argv[2]
sleeptime = int(sys.argv[3])
real_user_num = 0
listBestUsers = []
listWorstUsers = []

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(sleeptime):
            print("\nThread start")
            getAct()
            submitResult()


class User:
    userName = ""
    userAct1 = 0
    userAct2 = 0

    def __init__(self, userName, userAct1, userAct2):
        self.userName = userName
        self.userAct1 = userAct1
        self.userAct2 = userAct2


def getAct():
    global goldNum
    global closeUser
    global farUser
    global userNum
    global listUser
    global real_user_num
    # print('Hello Timer1!')

    # send request
    requestData = {"roomid":roomid, "key":secretKey}
    # print(requestData)
    # values = requests.get(url+"/getAct/",params=requestData)
    res = requests.get(url+"/getAct/", params=requestData)
    values = res.json()
    # print(values)
    userNum = values.get('userNum')
    real_user_num = userNum
    users = values.get('users')

    listUser = []
    # users=[{"userName":"abc","userAct":[1,2]},{"userName":"er","userAct":[6,7]}]  #测试代码

    # init
    for user in users:
        listUser.append(User(
            userName=user.get('userName'),
            userAct1=user.get("userAct")[0],
            userAct2=user.get("userAct")[1]
        ))
        if user.get("userAct")[0] == 0 and user.get("userAct")[1] == 0:
            if real_user_num > 0:
                real_user_num = real_user_num-1

    total = 0
    for user in listUser:
        total += user.userAct1
        total += user.userAct2
    if listUser:
        goldNum = (total / (real_user_num * 2))*0.618
    else:
        goldNum = 0

    close_num = 10000  # 最接近黄金数的数
    far_num = goldNum  # 离黄金数最远的

    for user in listUser:
        if real_user_num > 2:   # 寻找BestNum和WorstNum
            if abs(user.userAct1 - goldNum) < abs(close_num - goldNum):
                close_num = user.userAct1
                # closeUser = user.userName
            if abs(user.userAct2 - goldNum) < abs(close_num - goldNum):
                close_num = user.userAct2
                # closeUser = user.userName
            if abs(user.userAct1 - goldNum) > abs(far_num - goldNum):
                far_num = user.userAct1
                # farUser = user.userName
            if abs(user.userAct2 - goldNum) > abs(far_num - goldNum):
                far_num = user.userAct2
                # farUser = user.userName
    for user in listUser:
        if real_user_num > 2:
            if user.userAct1 == close_num or user.userAct2 == close_num:    # 输出close_num的用户
                listBestUsers.append(user.userName)
            if user.userAct1 == far_num or user.userAct2 == far_num:        # 输出far_num的用户
                listWorstUsers.append(user.userName)
    # 清除重复
    for user1 in listWorstUsers:
        for user2 in listWorstUsers:
            if user1 == user2:
                listWorstUsers.remove(user2)
    for user1 in listBestUsers:
        for user2 in listBestUsers:
            if user1 == user2:
                listBestUsers.remove(user2)

    # for test
    # print(goldNum)
    # print(closeUser,close_num)
    # print(farUser,far_num)

    if res.status_code == 200:
        print("GET success")


def submitResult():
    requestData = {"roomid": roomid, "key": secretKey}
    data = {"roundTime": sleeptime, "goldenNum": goldNum, "userNum": userNum, "users": []}

    if real_user_num > 2:
        for user in listUser:
            if user in listBestUsers:
                data.get("users").append({"userName": user.userName, "userScore": userNum - 2})
            elif user in listWorstUsers:
                data.get("users").append({"userName": user.userName, "userScore": -2})
            else:
                data.get("users").append({"userName": user.userName, "userScore": 0})
    else:
        if len(listUser) != 0:
            for user in listUser:
                data.get("users").append({"userName": user.userName, "userScore": 0})
        else:
            print("No User")

    data_json = json.dumps(data)
    r = requests.post(url+"/submitResult/", params=requestData, data=data_json)
    if r.status_code == 200:
        print("POST success")


if __name__ == "__main__":
    stopFlag = Event()
    thread = MyThread(stopFlag)
    thread.start()

    # this will stop the timer
    # stopFlag.set()
