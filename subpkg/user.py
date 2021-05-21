import asyncio
import time
import json
import requests
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

async def run(loop):
    # Use borrowed connection for NATS then mount NATS Streaming
    # client on top.
    
    URL = "nats://defaultFissionAuthToken@nats-streaming.fission:4222"
    clusterID = "fissionMQTrigger"
    clientID = "clientSub"
    subj = "test1"

    nc = NATS()
    await nc.connect(io_loop=loop, servers=[URL])

    # Start session with NATS Streaming cluster.
    sc = STAN()
    await sc.connect(clusterID, clientID, nats=nc)

    future = asyncio.Future(loop=loop)
    async def cb(msg):
        nonlocal future
        # print("Received a message (seq={}): {}".format(msg.seq, msg.data))
        decoded = json.loads(msg.data)
        decoded['end'] = time.time()
        decoded['duration'] = decoded['end'] - decoded['start']
        decoded['e2e_duration'] = decoded['end'] - decoded['trigger']
        # print("Received dict: {}".format(decoded))
        future.set_result(decoded)

    # Subscribe to get all messages since beginning.
    sub = await sc.subscribe(subj, start_at='last_received', cb=cb)
    await asyncio.wait_for(future, 10, loop=loop)

    # Stop receiving messages
    await sub.unsubscribe()

    # Close NATS Streaming session
    await sc.close()

    # We are using a NATS borrowed connection so we need to close manually.
    await nc.close()

    return future.result()

def send(data):
    # receive msg service url
    url = ""
    response = requests.post(url, json.dumps(data))
    if response.status_code is not 200:
        return False
    return True

def main():
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(run(loop))
    loop.close()
    if not send(result):
        print("send result to file failed.")
    return json.dumps(result)