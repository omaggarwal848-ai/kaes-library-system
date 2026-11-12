"""
Manual Stack Data Structure Implementation for Book Return Management.
Follows LIFO (Last In, First Out) principle using a Python class and a Python list.
"""

class StackEmptyException(Exception):
    """Exception raised when an operation is performed on an empty stack."""
    pass


class BookReturnStack:
    """
    A manual implementation of a LIFO Stack using Python's built-in list.
    Used to manage returned books awaiting re-shelving and inspection.
    """
    def __init__(self):
        # Internal container: Pure Python list
        self._items = []

    def push(self, item):
        """
        Push a returned book record onto the top of the stack.
        Time Complexity: O(1)
        """
        if item is None:
            raise ValueError("Cannot push None onto stack.")
        self._items.append(item)
        return True

    def pop(self):
        """
        Remove and return the top-most (most recently returned) book from the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise StackEmptyException("Stack Underflow: No returned books currently in the stack.")
        return self._items.pop()

    def peek(self):
        """
        Inspect the top-most book on the stack without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self):
        """
        Check whether the stack contains any items.
        """
        return len(self._items) == 0

    def size(self):
        """
        Return the total number of books currently on the stack.
        """
        return len(self._items)

    def display(self):
        """
        Return all items in LIFO order (top of stack first, bottom of stack last).
        """
        return list(reversed(self._items))

    def clear(self):
        """
        Clear all items from the stack.
        """
        self._items = []

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        # Iterates from top of stack to bottom (LIFO)
        return iter(reversed(self._items))

    def __repr__(self):
        return f"<BookReturnStack(size={self.size()}, top={self.peek()})>"
