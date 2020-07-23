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

"""Commonly used utilities."""


def timedelta(t_0, t_1):
    """Returns the time difference (in seconds) between two protobuf timestamps."""
    return t_1.seconds - t_0.seconds + 1.0e-9 * (t_1.nanos - t_0.nanos)


class QueueIterator:
    """Provides an iterator interface for the builtin Queue type. Each iteration yields
    queue.get(block, timeout) (which may raise an Empty exception); the destructor calls
    the callback provided with on_iterclose.

    Parameters
    ----------
    queue : Queue
        The queue to poll for items.
    block : bool (default: True)
        Whether to block when the queue is empty (block argument of Queue.get()).
    timeout : float (default: None)
        Max. amount of time to wait for a queue item (timeout argument of Queue.get()).
    on_iterclose : function with 0 parameters (default: None)
        Function to call when the object is deleted.
    """
    def __init__(self, queue, block=True, timeout=None, on_iterclose=None):
        self._queue = queue
        self._block = block
        self._timeout = timeout
        self._on_iterclose = on_iterclose

    def __iter__(self):
        while True:
            yield self._queue.get(self._block, self._timeout)

    def __del__(self):
        if self._on_iterclose is not None:
            self._on_iterclose()
