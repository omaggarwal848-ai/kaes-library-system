from django.utils import timezone
from .stack_ds import BookReturnStack, StackEmptyException
from .models import ReturnStackItem
from transactions.models import ActivityLog

class StackService:
    """
    Singleton service managing the in-memory manual Python Stack
    and synchronizing it with database persistence.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StackService, cls).__new__(cls)
            cls._instance.stack = BookReturnStack()
            cls._instance._initialized = False
        return cls._instance

    def initialize_stack(self):
        """Loads pending 'in_stack' items from database into the Python list stack in LIFO order."""
        self.stack.clear()
        # Order by ascending pushed_at/id so the earliest item is at index 0 and latest is at top (-1)
        pending_items = ReturnStackItem.objects.filter(status='in_stack').order_by('id')
        for item in pending_items:
            self.stack.push(item.to_dict())
        self._initialized = True

    def get_stack(self):
        if not self._initialized:
            self.initialize_stack()
        return self.stack

    def push(self, book_return, user=None):
        """Pushes a return onto the Python stack and persists it."""
        issue = book_return.issue
        item = ReturnStackItem.objects.create(
            book_return=book_return,
            book_title=issue.book.title,
            book_isbn=issue.book.isbn,
            student_name=issue.student.full_name,
            student_id=issue.student.student_id,
            condition=book_return.book_condition,
            status='in_stack',
            notes=book_return.remarks
        )
        self.get_stack().push(item.to_dict())

        # Log Activity
        ActivityLog.objects.create(
            user=user,
            action_type='STACK_PUSH',
            description=f"Pushed returned book '{issue.book.title}' onto Return Stack (Current Stack Size: {self.stack.size()})."
        )
        return item

    def pop(self, user=None):
        """
        Pops the top returned book from the manual Python stack and marks it as reshelved.
        """
        stack = self.get_stack()
        if stack.is_empty():
            raise StackEmptyException("Cannot POP: The Return Stack is currently empty.")

        popped_dict = stack.pop()
        item_id = popped_dict.get('id')

        # Update in database
        try:
            item_db = ReturnStackItem.objects.get(id=item_id)
            item_db.status = 'shelved'
            item_db.popped_at = timezone.now()
            item_db.popped_by = user if user and user.is_authenticated else None
            item_db.save()
        except ReturnStackItem.DoesNotExist:
            pass

        # Log Activity
        ActivityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action_type='STACK_POP',
            description=f"Popped '{popped_dict.get('book_title')}' from Return Stack for re-shelving. (Remaining in Stack: {stack.size()})."
        )
        return popped_dict

    def peek(self):
        """Peeks at top item without removing."""
        return self.get_stack().peek()

    def display(self):
        """Returns all items currently in stack from top to bottom (LIFO)."""
        return self.get_stack().display()

    def size(self):
        return self.get_stack().size()

    def get_history(self, limit=50):
        """Returns full historical return stack items."""
        return ReturnStackItem.objects.all().order_by('-id')[:limit]

# Global instance
stack_service = StackService()
