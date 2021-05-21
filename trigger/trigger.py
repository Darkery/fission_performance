import requests
import json
import time

def send(msgId):
    # Need to add your host
    host = ""
    url = host + "pub?msgId=" + str(msgId) +"&trigger=" + str(time.time())
    print(url)
    response = requests.get(url)
    print(response)

if __name__ == '__main__':
    for i in range(20):
        send(i)
        time.sleep(1)