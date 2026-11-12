import uuid
from django.utils import timezone
from .queue_ds import BookRequestQueue, QueueEmptyException
from .models import BookRequest
from transactions.models import ActivityLog

class QueueService:
    """
    Singleton service managing the in-memory manual Python Queue (collections.deque)
    and synchronizing it with database persistence and notification rules.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueueService, cls).__new__(cls)
            cls._instance.queue = BookRequestQueue()
            cls._instance._initialized = False
        return cls._instance

    def initialize_queue(self):
        """Loads all pending requests from DB into the Python collections.deque queue in FIFO order."""
        self.queue.clear()
        pending_requests = BookRequest.objects.filter(status='pending').order_by('request_date')
        for req in pending_requests:
            self.queue.enqueue(req.to_dict())
        self._initialized = True

    def get_queue(self):
        if not self._initialized:
            self.initialize_queue()
        return self.queue

    def enqueue(self, student, book, remarks="", user=None):
        """
        Enqueues a new hold request for a book in FIFO order.
        """
        request_id = f"REQ-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        req_obj = BookRequest.objects.create(
            request_id=request_id,
            student=student,
            book=book,
            status='pending',
            remarks=remarks
        )

        self.get_queue().enqueue(req_obj.to_dict())

        # Log Activity
        ActivityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action_type='QUEUE_ENQUEUE',
            description=f"Enqueued hold request {request_id} from {student.full_name} for '{book.title}' (Queue Size: {self.queue.size()})."
        )
        return req_obj

    def dequeue(self, user=None, status='approved'):
        """
        Dequeues the front-most (oldest pending) request from the Python deque
        and marks it approved/ready for pickup, generating notification.
        """
        queue = self.get_queue()
        if queue.is_empty():
            raise QueueEmptyException("Cannot DEQUEUE: The Book Request Queue is currently empty.")

        dequeued_dict = queue.dequeue()
        req_id = dequeued_dict.get('id')

        try:
            req_db = BookRequest.objects.get(id=req_id)
            req_db.status = status
            req_db.processed_at = timezone.now()
            req_db.processed_by = user if user and user.is_authenticated else None
            req_db.notification_sent = True
            req_db.notification_message = (
                f"Good news, {req_db.student.first_name}! Your requested book '{req_db.book.title}' "
                f"is now ready for collection at the library counter."
            )
            req_db.save()
        except BookRequest.DoesNotExist:
            pass

        # Log Activity
        ActivityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action_type='QUEUE_DEQUEUE',
            description=f"Dequeued request {dequeued_dict.get('request_id')} for '{dequeued_dict.get('book_title')}'. Student {dequeued_dict.get('student_name')} notified. (Remaining in Queue: {queue.size()})."
        )
        return dequeued_dict

    def peek(self):
        """Peek at the front request in the queue."""
        return self.get_queue().peek()

    def peek_rear(self):
        """Peek at the rear request in the queue."""
        return self.get_queue().peek_rear()

    def display(self):
        """Returns all items in FIFO order (Front to Rear)."""
        return self.get_queue().display()

    def size(self):
        return self.get_queue().size()

    def notify_if_book_available(self, book):
        """
        When a book is returned or copies are added, check if anyone in the queue
        is waiting for this book and notify the first eligible student (FIFO).
        """
        queue = self.get_queue()
        # Find first matching in queue
        pending_for_book = BookRequest.objects.filter(book=book, status='pending').order_by('request_date').first()
        if pending_for_book and book.available_copies > 0:
            # Reinitialize or dequeue specific
            pending_for_book.status = 'approved'
            pending_for_book.notification_sent = True
            pending_for_book.notification_message = (
                f"Alert: '{book.title}' has just been returned and is reserved for you at the library desk!"
            )
            pending_for_book.processed_at = timezone.now()
            pending_for_book.save()
            self.initialize_queue()
            return pending_for_book
        return None

# Global instance
queue_service = QueueService()
