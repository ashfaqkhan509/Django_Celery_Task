# Django_Celery_Task

This project demonstrates asynchronous background task processing using 
**Django**, **Celery**, and **Redis**, with automated email sending,
PDF invoice generation, image processing, and periodic tasks.

## Features
- **Send Welcome Emails** – Sends a welcome email to new users.
- **Send Invoice Emails** – Generates PDF invoices and emails them to customers.
- **Daily Summary Emails** – Sends daily activity summary emails to all users (using `django-celery-beat`).
- **Image Processing** – Processes uploaded user profile images into multiple sizes (thumbnail, medium, large).
- **Celery Task Retries** – Automatic retry for failed tasks (e.g., email sending errors).
- **Comprehensive Test Suite** – Unit tests for all Celery tasks with coverage reporting.

## 🚀 Getting Started

### 🔧 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/ashfaqkhan509/Django_Celery_Task.git
cd Django_Celery_Task

# Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

