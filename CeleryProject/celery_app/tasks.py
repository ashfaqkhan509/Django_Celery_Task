from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import Order, UserProfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
import io
import os
from PIL import Image


@shared_task(bind=True)
def send_welcome_email(self, user_email, username):
    """
    Send a welcome email to a newly registered user.
    
    Args:
        user_email and username: The ID of the user to send the email to
    """
    try:
        subject = "Welcome to Our Platform!"
        message = f"Hello {username},\n\nWelcome to our platform!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        send_mail(
            subject,
            message,
            from_email,
            recipient_list
        )
    except Exception as error:
        raise self.retry(exc=error, countdown=60, max_retries=3)


@shared_task(bind=True)
def send_invoice_email(self, order_id):
    """
    Generate a PDF invoice and email it to the customer.
    
    Args:
        order_id (int): The ID of the order to generate invoice for
    """

    try:
        order = Order.objects.get(id=order_id)

        # Generate PDF using ReportLab
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.setFont("Helvetica", 12)
        p.drawString(100, height - 50, f"Invoice for Order #{order.id}")
        p.drawString(100, height - 100, f"Customer: {order.user.get_full_name()} ({order.user.email})")
        p.drawString(100, height - 130, f"Product: {order.product_name}")
        p.drawString(100, height - 160, f"Price: ${order.price}")
        p.drawString(100, height - 190, f"Date: {order.created_at.strftime('%Y-%m-%d')}")

        p.showPage()
        p.save()

        buffer.seek(0)

        # Prepare email
        email = EmailMessage(
            subject=f'Invoice for Order #{order.id}',
            body='Attached is your invoice.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        email.attach(f'invoice_{order.id}.pdf', buffer.read(), 'application/pdf')
        email.send()
    except Exception as error:
        raise self.retry(exc=error, countdown=60, max_retries=3)


@shared_task
def send_daily_summary_emails():
    """
    Send daily summary emails to all users.
    This task is scheduled to run daily via django-celery-beat.
    """
    users = User.objects.all()
    
    for user in users:
        send_mail(
            subject='Your Daily Activity',
            message=f'Hello {user.username}, here is your daily activity summary.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    return f"Sent daily summary emails to {users.count()} users."


@shared_task(bind=True)
def process_image(self, user_profile_id):
    """
    Process uploaded user image by creating multiple resized versions.
    
    Args:
        user_profile_id (int): ID of the user who uploaded the image
    """
    try:
        user_profile = UserProfile.objects.get(id=user_profile_id)
        original_image_path = user_profile.image.path
        original_image = Image.open(original_image_path)
        
        sizes = {
            'thumbnail': (100, 100),
            'medium': (300, 300),
            'large': (600, 600)
        }
        
        for size_name, size in sizes.items():
            # Create resized image
            resized_image = original_image.copy()
            resized_image.thumbnail(size)
            
            # Prepare save path
            original_image_dir = os.path.dirname(original_image_path)
            resize_image_dir = os.path.join(os.path.dirname(original_image_dir), size_name)
            os.makedirs(resize_image_dir, exist_ok=True)
            
            # Save resized image
            filename = os.path.basename(original_image_path)
            save_path = os.path.join(resize_image_dir, filename)
            resized_image.save(save_path)
            
            print(f"Saved {size_name} version at {save_path}")
            
        return f"Successfully processed image for user {user_profile_id}"
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
