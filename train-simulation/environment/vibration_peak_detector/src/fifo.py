import numpy as np


class Fifo:
    def __init__(self, capacity):
        """
        Create fifo with <capacity> entries
        <capacity> specifies the dimensions of the fifo, e.g.
        10 - for a 1D array with 10 entries
        (10,2) - for a 2D array with 10 entries with 2 columns
        """
        self._fifo = np.zeros(capacity)
        self._capacity = capacity[0] if type(capacity) is tuple else capacity
        self._entries = 0

    def entries(self):
        return self._entries

    def free_entries(self):
        return self._capacity - self._entries

    def push(self, nparr):
        """
        add nparr to fifo. Must fit to shape of created fifo.
        Oldest sample must be in nparr[0]
        @raise: BufferError if not enough space in fifo
        """
        shape = np.shape(nparr)
        in_len = shape[0]
        if in_len > self.free_entries():
            raise BufferError("fifo overflow")

        self._fifo[self._entries : self._entries + in_len] = nparr  # noqa E203
        self._entries += in_len

    def pop(self, n):
        """
        pop n entries from fifo.
        @raise: BufferError if not enough entries in fifo
        """
        rv = self.peek(n)
        self._fifo = np.roll(self._fifo, -n, axis=0)
        self._entries -= n
        return rv

    def peek(self, n):
        """
        peek first n entries from fifo. Don't remove entries from fifo.
        @raise: BufferError if not enough entries in fifo
        """
        if self._entries < n:
            raise BufferError(
                f"not enough entries in fifo. Requested {n}, in fifo: {self._entries}"
            )
        return self._fifo[:n]

    def clear(self):
        self._entries = 0
