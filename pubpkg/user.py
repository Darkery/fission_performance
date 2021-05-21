import asyncio
import time
import json
from flask import request
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

async def run(loop, msg_id, trigger):
    # Use borrowed connection for NATS then mount NATS Streaming
    # client on top.
    
    URL = "nats://defaultFissionAuthToken@nats-streaming.fission:4222"
    clusterID = "fissionMQTrigger"
    clientID = "clientPub"
    subj = "test1"

    nc = NATS()
    await nc.connect(io_loop=loop, servers=[URL])

    # Start session with NATS Streaming cluster.
    sc = STAN()
    await sc.connect(clusterID, clientID, nats=nc)

    # Synchronous Publisher, does not return until an ack
    # has been received from NATS Streaming.

    timestamp = time.time()
    msg = {'msg_id': msg_id, 'trigger': float(trigger), 'start': timestamp}
    encoded = json.dumps(msg).encode('utf-8')
    await sc.publish(subj, encoded)


    # Close NATS Streaming session
    await sc.close()

    # We are using a NATS borrowed connection so we need to close manually.
    await nc.close()

def main():
    msg_id = request.args.get('msgId')
    trigger = request.args.get('trigger')
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run(loop, msg_id, trigger))
    loop.close()
    return "Send Msg id" + str(msg_id)