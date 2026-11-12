"""
Manual Queue Data Structure Implementation for Book Request Management.
Follows FIFO (First In, First Out) principle using a Python class and collections.deque.
"""

from collections import deque

class QueueEmptyException(Exception):
    """Exception raised when an operation is performed on an empty queue."""
    pass


class BookRequestQueue:
    """
    A manual implementation of a FIFO Queue using Python's collections.deque.
    Used to manage student book hold requests in strict FIFO order.
    """
    def __init__(self):
        # Internal container: collections.deque
        self._queue = deque()

    def enqueue(self, item):
        """
        Add a new book request to the rear/tail of the queue.
        Time Complexity: O(1)
        """
        if item is None:
            raise ValueError("Cannot enqueue None onto queue.")
        self._queue.append(item)
        return True

    def dequeue(self):
        """
        Remove and return the front-most (oldest pending) request from the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise QueueEmptyException("Queue Underflow: No pending book requests in the queue.")
        return self._queue.popleft()

    def peek(self):
        """
        Inspect the front-most request (next to be served) without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._queue[0]

    def peek_rear(self):
        """
        Inspect the most recently enqueued request at the rear of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._queue[-1]

    def is_empty(self):
        """
        Check if the queue is empty.
        """
        return len(self._queue) == 0

    def size(self):
        """
        Return the total number of pending requests in the queue.
        """
        return len(self._queue)

    def display(self):
        """
        Return all requests in FIFO order (Front / Head first to Rear / Tail last).
        """
        return list(self._queue)

    def clear(self):
        """
        Clear all items from the queue.
        """
        self._queue.clear()

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        # Iterates from Front to Rear (FIFO)
        return iter(self._queue)

    def __repr__(self):
        return f"<BookRequestQueue(size={self.size()}, front={self.peek()})>"
