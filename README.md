# kaes - Modern Full-Stack Library Management System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Pandas](https://img.shields.io/badge/Pandas-3.1-orange.svg)](https://pandas.pydata.org/)

**kaes** is a modern, responsive, and complete Library Management System built with Python Full-Stack Architecture, Django, Bootstrap 5, Chart.js, and Pandas. It features authentic manual implementations of classic Data Structures (**LIFO Stack** for Book Returns and **FIFO Queue** using `collections.deque` for Hold Requests), a glassmorphism SaaS UI, real-time analytics, and CSV bulk processing.

---

## 🚀 Key Features

1. **Modern SaaS Glassmorphism UI / UX**
   - Translucent glassmorphic panels and dark/light mode toggle.
   - Navy blue, purple, white, and soft slate color palette.
   - Fully responsive for mobile, tablet, and desktop screens.
   - Interactive Chart.js analytics for catalog distribution and 6-month borrowing trends.

2. **Role-Based Authentication & Dashboards**
   - **Admin / Librarian Dashboard**: Real-time statistics, inventory management, circulation desk, CSV manager, activity audit logs.
   - **Student Portal**: Active loans counter, overdue warnings, dynamic fine calculations, queue wait-order tickets, book hold requests.

3. **Data Structure: Manual Python Stack (LIFO)**
   - Located at `returns_stack/stack_ds.py`.
   - Manages returned books placed on the return/inspection desk prior to re-shelving.
   - Standard LIFO operations: `push()`, `pop()`, `peek()`, `display()`, `size()`, `is_empty()`.
   - Dedicated visual 3D cylinder representation in the UI with animated top-of-stack indicator.

4. **Data Structure: Manual Python Queue (FIFO)**
   - Located at `requests_queue/queue_ds.py` using `collections.deque`.
   - Handles student hold requests for out-of-stock and popular titles.
   - Standard FIFO operations: `enqueue()`, `dequeue()`, `peek()`, `display()`, `size()`, `is_empty()`.
   - Dedicated visual pipeline track displaying `FRONT / HEAD` and `REAR / TAIL` markers.
   - Automatic notification triggers when a returned book becomes available for queued students.

5. **Pandas CSV Import & Export System**
   - Bulk upload of Books and Students with schema validation, missing data reporting, and duplicate ISBN detection.
   - Export downloadable CSVs for Books, Students, Active Loans, Returned Books, and Requests.
   - Pre-packaged sample CSV files ready for testing in `sample_data/`.

---

## 🔑 Default Credentials

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| **Chief Librarian (Admin)** | `admin` | `admin123` | Full administrative control & data structure tools |
| **Student** | `student` | `student123` | Student portal, active loans & hold requests |

*(Both accounts are pre-seeded and accessible via 1-Click Demo buttons on the Sign In page).*

---

## 🛠️ Quick Installation & Setup

1. **Clone or Navigate to the Project:**
   ```bash
   cd C:\Users\LENOVO\.gemini\antigravity\scratch\kaes
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Database Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Seed Sample Data:**
   ```bash
   python manage.py seed_data
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
   Open your browser at `http://127.0.0.1:8000/`.

---

## 📁 Project Architecture

```
kaes/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── library_project/      # Project settings, root urls, wsgi
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/             # Authentication, UserProfile, Signals, Dashboard views
├── books/                # Book & Category models, CRUD, live search
├── students/             # Student model, borrowing summaries, directory
├── transactions/         # BookIssue, BookReturn, Circulation, ActivityLog
├── returns_stack/        # Manual Python Stack (LIFO), visual UI, services
├── requests_queue/       # Manual Python Queue (FIFO), visual pipeline, services
├── csv_manager/          # Pandas CSV bulk import, export, and validator
│
├── sample_data/          # Sample CSV test files for Books & Students
├── templates/            # Glassmorphism HTML templates
├── static/               # CSS styles and JavaScript visualizers
└── media/                # Uploaded covers and avatars
```
