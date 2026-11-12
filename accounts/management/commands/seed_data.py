from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import UserProfile
from books.models import Category, Book
from students.models import Student
from transactions.models import BookIssue, BookReturn, ActivityLog
from returns_stack.services import stack_service
from requests_queue.services import queue_service

class Command(BaseCommand):
    help = "Seeds database with comprehensive initial sample data for Kaes Library Management System."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Kaes database seeding..."))

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kaes-library.edu',
                'first_name': 'Chief',
                'last_name': 'Librarian',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))
        else:
            admin_user.set_password('admin123')
            admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'admin'
        admin_profile.phone = '+1-800-555-0199'
        admin_profile.bio = 'Chief Library Administrator and Catalog Curator.'
        admin_profile.save()

        # 2. Create Student User Accounts
        student_user, s_created = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@campus.edu',
                'first_name': 'Aarav',
                'last_name': 'Sharma',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if s_created:
            student_user.set_password('student123')
            student_user.save()
            self.stdout.write(self.style.SUCCESS("Created student user: student / student123"))
        else:
            student_user.set_password('student123')
            student_user.save()

        s_profile, _ = UserProfile.objects.get_or_create(user=student_user)
        s_profile.role = 'student'
        s_profile.phone = '+1-555-0144'
        s_profile.save()

        # 3. Create Categories
        categories_data = [
            ("Computer Science", "Core algorithms, computation theory, and architecture", "fa-laptop-code"),
            ("Artificial Intelligence", "Machine learning, neural networks, and modern AI systems", "fa-brain"),
            ("Programming Languages", "Python, Java, C++, Rust, Go, and software craftsmanship", "fa-code"),
            ("Data Engineering", "Distributed storage, databases, stream processing, pipelines", "fa-database"),
            ("Web Development", "Modern frontend, full-stack frameworks, reactive UI", "fa-globe"),
            ("Cybersecurity", "Network defense, cryptography, penetration testing", "fa-shield-halved"),
            ("Mathematics", "Discrete mathematics, linear algebra, probability, calculus", "fa-square-root-variable"),
            ("Electronics & Hardware", "Microcontrollers, embedded systems, VLSI, robotics", "fa-microchip"),
        ]

        cats = {}
        for name, desc, icon in categories_data:
            cat_obj, _ = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon}
            )
            cats[name] = cat_obj

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(cats)} categories."))

        # 4. Create Books
        books_data = [
            {
                "isbn": "978-0132350884",
                "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                "author": "Robert C. Martin",
                "category": cats["Programming Languages"],
                "publisher": "Prentice Hall",
                "publication_year": 2008,
                "edition": "1st Edition",
                "total_copies": 5,
                "available_copies": 3,
                "shelf_location": "Rack PL-01",
                "description": "A handbook of agile software craftsmanship, emphasizing readable, maintainable, and elegant code design."
            },
            {
                "isbn": "978-0262033848",
                "title": "Introduction to Algorithms",
                "author": "Thomas H. Cormen, Charles E. Leiserson",
                "category": cats["Computer Science"],
                "publisher": "MIT Press",
                "publication_year": 2009,
                "edition": "3rd Edition",
                "total_copies": 6,
                "available_copies": 4,
                "shelf_location": "Rack CS-01",
                "description": "The quintessential comprehensive textbook covering algorithmic design, asymptotic notation, and graph algorithms."
            },
            {
                "isbn": "978-1449355730",
                "title": "Learning Python: Powerful Object-Oriented Programming",
                "author": "Mark Lutz",
                "category": cats["Programming Languages"],
                "publisher": "O'Reilly Media",
                "publication_year": 2013,
                "edition": "5th Edition",
                "total_copies": 4,
                "available_copies": 2,
                "shelf_location": "Rack PL-02",
                "description": "Comprehensive, in-depth tutorial to the core Python language with extensive real-world exercises."
            },
            {
                "isbn": "978-1491957660",
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "category": cats["Data Engineering"],
                "publisher": "O'Reilly Media",
                "publication_year": 2017,
                "edition": "1st Edition",
                "total_copies": 5,
                "available_copies": 0, # Intentionally 0 to showcase queue requests!
                "shelf_location": "Rack DB-01",
                "description": "The definitive deep-dive guide to consistency models, replication, partitioning, and batch/stream processing."
            },
            {
                "isbn": "978-1119547259",
                "title": "Artificial Intelligence: A Modern Approach",
                "author": "Stuart Russell, Peter Norvig",
                "category": cats["Artificial Intelligence"],
                "publisher": "Pearson",
                "publication_year": 2020,
                "edition": "4th Edition",
                "total_copies": 4,
                "available_copies": 0, # Intentionally 0 to showcase queue requests!
                "shelf_location": "Rack AI-01",
                "description": "Leading textbook in AI explaining search, knowledge representation, probabilistic inference, and deep reinforcement learning."
            },
            {
                "isbn": "978-0134685991",
                "title": "Effective Java",
                "author": "Joshua Bloch",
                "category": cats["Programming Languages"],
                "publisher": "Addison-Wesley",
                "publication_year": 2017,
                "edition": "3rd Edition",
                "total_copies": 4,
                "available_copies": 3,
                "shelf_location": "Rack PL-03",
                "description": "Essential best-practice patterns and antipatterns for professional enterprise Java developers."
            },
            {
                "isbn": "978-0201616224",
                "title": "The Pragmatic Programmer",
                "author": "Andrew Hunt, David Thomas",
                "category": cats["Computer Science"],
                "publisher": "Addison-Wesley",
                "publication_year": 2019,
                "edition": "20th Anniversary Edition",
                "total_copies": 5,
                "available_copies": 4,
                "shelf_location": "Rack CS-02",
                "description": "Classic principles on career mastery, orthogonality, pragmatic philosophy, and debugging techniques."
            },
            {
                "isbn": "978-0131103627",
                "title": "The C Programming Language",
                "author": "Brian W. Kernighan, Dennis M. Ritchie",
                "category": cats["Programming Languages"],
                "publisher": "Prentice Hall",
                "publication_year": 1988,
                "edition": "2nd Edition",
                "total_copies": 3,
                "available_copies": 2,
                "shelf_location": "Rack PL-04",
                "description": "The authoritative classic reference written by the inventor of C and Unix pioneer."
            },
            {
                "isbn": "978-1492041139",
                "title": "Fluent Python",
                "author": "Luciano Ramalho",
                "category": cats["Programming Languages"],
                "publisher": "O'Reilly Media",
                "publication_year": 2022,
                "edition": "2nd Edition",
                "total_copies": 4,
                "available_copies": 3,
                "shelf_location": "Rack PL-05",
                "description": "Clear hands-on guide to idiomatic Python 3, metaprogramming, generators, and concurrency."
            },
            {
                "isbn": "978-0596517748",
                "title": "JavaScript: The Good Parts",
                "author": "Douglas Crockford",
                "category": cats["Web Development"],
                "publisher": "O'Reilly Media",
                "publication_year": 2008,
                "edition": "1st Edition",
                "total_copies": 3,
                "available_copies": 2,
                "shelf_location": "Rack WD-01",
                "description": "Scrapes away the cumbersome parts of JavaScript to reveal an exceptionally elegant functional programming language."
            },
            {
                "isbn": "978-1593279929",
                "title": "Automate the Boring Stuff with Python",
                "author": "Al Sweigart",
                "category": cats["Programming Languages"],
                "publisher": "No Starch Press",
                "publication_year": 2019,
                "edition": "2nd Edition",
                "total_copies": 4,
                "available_copies": 3,
                "shelf_location": "Rack PL-06",
                "description": "Practical programming for total beginners, automating tasks with web scraping, spreadsheets, and file operations."
            },
            {
                "isbn": "978-0321573513",
                "title": "Algorithms",
                "author": "Robert Sedgewick, Kevin Wayne",
                "category": cats["Computer Science"],
                "publisher": "Addison-Wesley",
                "publication_year": 2011,
                "edition": "4th Edition",
                "total_copies": 5,
                "available_copies": 3,
                "shelf_location": "Rack CS-03",
                "description": "Surveys the most important computer algorithms in use today with thorough mathematical analysis."
            }
        ]

        created_books = []
        for b_dict in books_data:
            book_obj, _ = Book.objects.get_or_create(
                isbn=b_dict["isbn"],
                defaults=b_dict
            )
            created_books.append(book_obj)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_books)} books."))

        # 5. Create Students
        students_data = [
            ("STU2024001", "Aarav", "Sharma", "aarav.sharma@campus.edu", "+91-98765-43210", "Computer Science & Engineering", 2024, student_user),
            ("STU2024002", "Ananya", "Iyer", "ananya.iyer@campus.edu", "+91-98765-43211", "Data Science & AI", 2024, None),
            ("STU2024003", "Rahul", "Verma", "rahul.verma@campus.edu", "+91-98765-43212", "Information Technology", 2023, None),
            ("STU2024004", "Priya", "Patel", "priya.patel@campus.edu", "+91-98765-43213", "Electronics & Communication", 2024, None),
            ("STU2024005", "Aditya", "Deshmukh", "aditya.deshmukh@campus.edu", "+91-98765-43214", "Mechanical Engineering", 2023, None),
            ("STU2024006", "Sneha", "Reddy", "sneha.reddy@campus.edu", "+91-98765-43215", "Computer Science & Engineering", 2024, None),
            ("STU2024007", "Rohan", "Gupta", "rohan.gupta@campus.edu", "+91-98765-43216", "Data Science & AI", 2023, None),
            ("STU2024008", "Kavya", "Nair", "kavya.nair@campus.edu", "+91-98765-43217", "Business Administration", 2024, None),
        ]

        created_students = []
        for sid, fname, lname, email, phone, dept, year, u_link in students_data:
            stu_obj, _ = Student.objects.get_or_create(
                student_id=sid,
                defaults={
                    'user': u_link,
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'phone': phone,
                    'department': dept,
                    'enrollment_year': year,
                    'status': 'active'
                }
            )
            created_students.append(stu_obj)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_students)} students."))

        # 6. Create Issues (Active, Overdue, Returned)
        today = timezone.now().date()
        
        # Issue 1: Alex Johnson has Clean Code (Issued recently, normal)
        iss1, _ = BookIssue.objects.get_or_create(
            issue_id="ISS-202611-0001",
            defaults={
                'book': created_books[0],
                'student': created_students[0],
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=5),
                'due_date': today + timedelta(days=9),
                'status': 'issued'
            }
        )

        # Issue 2: Sophia Chen has Learning Python (Overdue by 4 days to demonstrate fine calculation!)
        iss2, _ = BookIssue.objects.get_or_create(
            issue_id="ISS-202611-0002",
            defaults={
                'book': created_books[2],
                'student': created_students[1],
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=18),
                'due_date': today - timedelta(days=4),
                'status': 'issued',
                'fine_amount': Decimal('8.00'),
                'notes': 'Overdue notice sent.'
            }
        )

        # Issue 3: Liam Miller returned Introduction to Algorithms (pushed to return stack!)
        iss3, _ = BookIssue.objects.get_or_create(
            issue_id="ISS-202611-0003",
            defaults={
                'book': created_books[1],
                'student': created_students[2],
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=12),
                'due_date': today + timedelta(days=2),
                'return_date': today - timedelta(days=1),
                'status': 'returned'
            }
        )
        ret1, _ = BookReturn.objects.get_or_create(
            issue=iss3,
            defaults={
                'return_date': timezone.now() - timedelta(hours=5),
                'returned_to': admin_user,
                'book_condition': 'Good',
                'fine_collected': Decimal('0.00'),
                'remarks': 'Pushed to return inspection stack.'
            }
        )

        # Issue 4: Priya Patel returned Pragmatic Programmer (pushed to return stack!)
        iss4, _ = BookIssue.objects.get_or_create(
            issue_id="ISS-202611-0004",
            defaults={
                'book': created_books[6],
                'student': created_students[3],
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=10),
                'due_date': today + timedelta(days=4),
                'return_date': today,
                'status': 'returned'
            }
        )
        ret2, _ = BookReturn.objects.get_or_create(
            issue=iss4,
            defaults={
                'return_date': timezone.now() - timedelta(hours=1),
                'returned_to': admin_user,
                'book_condition': 'Good',
                'fine_collected': Decimal('0.00'),
                'remarks': 'Latest returned item on Stack Top.'
            }
        )

        # 7. Push returns to Stack Service
        stack_service.initialize_stack()
        if stack_service.size() == 0:
            stack_service.push(ret1, admin_user)
            stack_service.push(ret2, admin_user)
            self.stdout.write(self.style.SUCCESS(f"Pushed 2 returned books to LIFO Return Stack."))

        # 8. Create Hold Requests in Request Queue (for unavailable books)
        # Designing Data-Intensive Applications has 0 available copies
        queue_service.initialize_queue()
        if queue_service.size() == 0:
            queue_service.enqueue(created_students[0], created_books[3], remarks="Urgent study for Distributed Systems exam", user=student_user)
            queue_service.enqueue(created_students[4], created_books[3], remarks="Project research reference", user=admin_user)
            queue_service.enqueue(created_students[5], created_books[4], remarks="Required textbook for AI module", user=admin_user)
            self.stdout.write(self.style.SUCCESS(f"Enqueued 3 hold requests to FIFO Request Queue."))

        # 9. Create Activity Logs
        ActivityLog.objects.get_or_create(
            action_type='BOOK_ADDED',
            description="System initialized with standard academic catalog.",
            user=admin_user
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
