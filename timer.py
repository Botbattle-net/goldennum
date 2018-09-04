import threading
import requests
from threading import Event
from threading import Thread
url = "http://127.0.0.1"
closeUser = ""
farUser = ""
userNum = 0
listUser = []
goldNum = 0


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(0.5):
            print("my thread")
            getAct(1)
            submitResult(1)


class User:
    userName = ""
    userAct1 = 0
    userAct2 = 0

    def __init__(self, userName, userAct1, userAct2):
        self.userName = userName
        self.userAct1 = userAct1
        self.userAct2 = userAct2


def getAct(roomid:int):
    global goldNum
    global closeUser
    global farUser
    global userNum
    global listUser
    #print('Hello Timer1!')

    #send request AND THIS PART HASN'T BEAN TESTED
    requestData = {"roomid":roomid}
    values = requests.get(url+"/getAct/",params=requestData)
    userNum = values.get('userNum')
    users = values.get('users')

    listUser = []
    # users=[{"userName":"abc","userAct":[1,2]},{"userName":"er","userAct":[6,7]}]  #测试代码

    for user in users:
        listUser.append(User(userName=user.get('userName'),userAct1=user.get("userAct")[0],userAct2=user.get("userAct")[1]))
    total = 0
    for user in listUser:
        total += user.userAct1
        total += user.userAct2
    goldNum = (total / len(listUser))*0.618
    close_num = 10000  # 最接近黄金数的数
    closeUser = ""
    far_num = goldNum  # 离黄金数最远的
    farUser = ""
    for user in listUser:
        if abs(user.userAct1 - goldNum) < abs(close_num - goldNum):
            close_num = user.userAct1
            closeUser = user.userName
        if abs(user.userAct2 - goldNum) < abs(close_num - goldNum):
            close_num = user.userAct2
            closeUser = user.userName
        if abs(user.userAct1 - goldNum) > abs(far_num - goldNum):
            far_num = user.userAct1
            farUser = user.userName
        if abs(user.userAct2 - goldNum) > abs(far_num - goldNum):
            far_num = user.userAct2
            farUser = user.userName
    print(goldNum)
    print(closeUser,close_num)
    print(farUser,far_num)

    # if values.status_code == 200:
    #    print("success")


def submitResult (roomid: int):
    #print('Hello Timer2!')
    requestData = {"roomid":roomid}
    data = {"roundTime":60,"goldenNum": goldNum, "userNum": userNum, "users": []}
    for user in listUser:
        if user.userName == closeUser:
            data.get("users").append( {"userName":user.userName,"userScore":userNum} )
        elif user.userName == farUser:
            data.get("users").append({"userName": user.userName, "userScore": -2})
        else:
            data.get("users").append({"userName": user.userName, "userScore": 0})

    # print (data) # for test


    # HAS NOT BEEN TESTED!!
    r = requests.post(url+"/submitResult/", params=requestData, data=data)

    # if r.status_code == 200:
    #    print("success")

    
if __name__ == "__main__":
    stopFlag = Event()
    thread = MyThread(stopFlag)
    thread.start()

    # this will stop the timer
    #stopFlag.set()
