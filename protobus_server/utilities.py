def timedelta(t0, t1):
    return t1.seconds - t0.seconds + 1.0e-9 * (t1.nanos - t0.nanos)


class QueueIterator(object):
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
