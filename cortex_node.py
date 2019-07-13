#!/usr/bin/env python3

import socket
import asyncio
import time
import random
import cloudpickle
from os import getenv
from sys import stderr, stdout

from multiprocessing import Pool

from dotenv import load_dotenv

from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime

class CortexNode(Protocol):
    def __init__(self):
        load_dotenv()

        self.HOST = getenv('HOST')  # The server's hostname or IP address
        self.PORT = int(getenv('PORT'))        # The port used by the server
        self.USERNAME = getenv('USERNAME')
        self.SECRET_KEY = getenv('SECRET_KEY')
        self.connected = False
        self.client_id = -1

    def dataReceived(self, data):
        data = cloudpickle.loads(data)
        if 'GREETING' in data:
            greeting = data['GREETING']
            client_id = data['CLIENT_ID']
            self.client_id = client_id
            print('GREETING:', greeting)
            print('CLIENT_ID', client_id)
            packet = cloudpickle.dumps({
                'IP': socket.gethostbyname(socket.gethostname()),
                'CPU_COUNT': multiprocessing.cpu_count(),
                'DATETIME_CONNECTED': datetime.now(),
                'CLIENT_ID': self.client_id,
            })
            self.transport.write(packet)
        elif 'FUNC' in data:
            func = data['FUNC']
            arg = data['ARG']
            print('ARGS:', arg)
            with Pool(multiprocessing.cpu_count()) as p:
                results = p.map(func, arg)
                p.close()
                p.join()

            packet = cloudpickle.dumps({
                'CLIENT_ID': self.client_id,
                'RESULTS': results
            })
            self.transport.write(packet)
        else:
            print(data)


'''async def worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        arg = await queue.get()

        # Now that you have the arg, perform the func on it.

        # Notify the queue that the "work item" has been processed.
        queue.task_done()


async def processJobs():
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Generate random timings and put them into the queue.
    total_sleep_time = 0
    for _ in range(20):
        sleep_for = random.uniform(0.05, 1.0)
        total_sleep_time += sleep_for
        queue.put_nowait(sleep_for)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(3):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    print(f'total expected sleep time: {total_sleep_time:.2f} seconds')'''


def runCortexNode():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv('HOST'), int(getenv('PORT')))
    d = connectProtocol(endpoint, CortexNode())

    reactor.run()


if __name__ == '__main__':
    runCortexNode()
