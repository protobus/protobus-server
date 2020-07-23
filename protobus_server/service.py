# Copyright 2020 The protobus developers.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides the main protobus service."""

from concurrent.futures import ThreadPoolExecutor
import os
from queue import Queue
import re
import struct
import sys

import grpc

from utilities import QueueIterator, timedelta
from idl import protobus_rpc_pb2
from idl import protobus_rpc_pb2_grpc


def write_to_store(queue, dest_pattern):
    """Iterated over the queue and stores all messages according to the given configuration. Stops
    when None is encountered."""

    files = {}
    for event in QueueIterator(queue):
        if event is None:
            break

        dest_name = dest_pattern.replace("{topic}", event.topic) + ".pb"
        dest_file = files.get(dest_name, None)
        if dest_file is None:
            dest_file = open(dest_name, 'ba')
            files[dest_name] = dest_file

        dest_file.write(struct.pack("<I", event.ByteSize()))
        dest_file.write(event.SerializeToString())
        dest_file.flush()


class ProtobusService(protobus_rpc_pb2_grpc.ProtobusServiceServicer):
    """Main protobus service; see idl files for details."""

    def __init__(self, pool, store_root, store_patterns):
        self.queues = []

        for store_pattern in store_patterns:
            dest_pattern, regex = store_pattern.split(":")
            dest_pattern = os.path.join(store_root, dest_pattern)
            regex = re.compile(regex)
            queue = Queue()

            pool.submit(write_to_store, queue, dest_pattern)
            self.queues.append((regex, queue))

    def Publish(self, request_iterator, _):  # pylint: disable=invalid-name
        """Streaming interface which publishes protobus EncapsulatedEvent messages.
        See idl files for details."""

        for i, event in enumerate(request_iterator):
            event.server_receive_time.GetCurrentTime()
            event.payload_size = event.payload.ByteSize()

            delta = timedelta(event.client_event_time, event.server_receive_time)
            if i % 1 == 0:
                print(f"{event.client_event_time.seconds}.{event.client_event_time.nanos:09d}"
                      f"({1000 * delta:+.1f} ms) "
                      f"{event.topic} {','.join(f'{k}={v}' for k, v in event.tags.items())} "
                      f"{event.payload.type_url} [{event.payload_size}]", file=sys.stderr)

            for regex, queue in self.queues:
                if regex.match(event.topic):
                    queue.put(event)

        return protobus_rpc_pb2.Status(code=protobus_rpc_pb2.Code.OK, message="OK")

    def Subscribe(self, request, _):  # pylint: disable=invalid-name
        """Streaming interface which returns all EncapsulatedEvent messages matching the
        given SubscribeRequest."""

        def cleanup():
            self.queues.remove((regex, queue))

        regex = re.compile("|".join(request.topics))
        queue = Queue()
        self.queues.append((regex, queue))
        for event in QueueIterator(queue, on_iterclose=cleanup):
            yield event

    def stop(self):
        """Sends tombstones down all queues to shut down subscriptions and store writers."""

        for _, queue in self.queues:
            queue.put(None)


def serve(address, thread_pool_workers, store_root, store_patterns):
    """Sets up a concurrency thread pool and starts the gRPC service with the given store
    configuration."""

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
