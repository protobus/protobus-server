from utilities import QueueIterator, timedelta
from idl import protobus_rpc_pb2
from idl import protobus_rpc_pb2_grpc

from concurrent.futures import ThreadPoolExecutor
import os
from queue import Queue
import re
import struct
import sys

import grpc


def write_to_store(queue, dest_pattern):
    files = {}
    for event in QueueIterator(queue):
        if event is None:
            break

        dest = dest_pattern.replace("{topic}", event.topic)
        f = files.get(dest, None)
        if f is None:
            f = open(dest, 'ba')
            files[dest] = f

        f.write(struct.pack("<I", event.ByteSize()))
        f.write(event.SerializeToString())
        f.flush()


class ProtobusService(protobus_rpc_pb2_grpc.ProtobusServiceServicer):
    def __init__(self, pool, store_root, store_patterns):
        self.queues = []

        for store_pattern in store_patterns:
            dest_pattern, regex = store_pattern.split("=")
            dest_pattern = os.path.join(store_root, dest_pattern)
            regex = re.compile(regex)
            queue = Queue()

            pool.submit(write_to_store, queue, dest_pattern)
            self.queues.append((regex, queue))

    def Publish(self, events, context):
        for i, event in enumerate(events):
            event.server_receive_time.GetCurrentTime()
            event.payload_size = event.payload.ByteSize()

            dt = timedelta(event.client_event_time, event.server_receive_time)
            if i % 1 == 0:
                print(f"{event.client_event_time.seconds}.{event.client_event_time.nanos:09d}({1000 * dt:+.1f} ms)"
                      f"{event.topic} {','.join(f'{k}={v}' for k, v in event.tags.items())}"
                      f"{event.payload.type_url} [{event.payload_size}]", file=sys.stderr))

            for regex, queue in self.queues:
                if regex.match(event.topic):
                    queue.put(event)

        return protobus_rpc_pb2.Status(code=protobus_rpc_pb2.Code.OK, message="OK")

    def Subscribe(self, request, context):
        def cleanup():
            self.queues.remove((regex, queue))

        regex = re.compile("|".join(request.topics))
        queue = Queue()
        self.queues.append((regex, queue))
        for event in QueueIterator(queue, on_iterclose=cleanup):
            yield event

    def stop(self):
        for regex, queue in self.queues:
            queue.put(None)


def serve(address, thread_pool_workers, store_root, store_patterns):
    if not os.path.isdir(store_root):
        print("Store root does not exist.", file=sys.stderr)
        sys.exit(1)

    pool = ThreadPoolExecutor(max_workers=thread_pool_workers)

    server = grpc.server(pool)
    service = ProtobusService(pool, store_root, store_patterns)

    protobus_rpc_pb2_grpc.add_ProtobusServiceServicer_to_server(service, server)

    server.add_insecure_port(address)
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down...", file=sys.stderr)
        server.stop(1)  # Stop with 1 s grace period
        server.wait_for_termination()
        service.stop()
