from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from .models import UserProfile, Order
from django.conf import settings
from .tasks import (
    send_welcome_email,
    send_invoice_email,
    send_daily_summary_emails,
    process_image
)
import tempfile
import os
from PIL import Image
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile


class CeleryTaskTest(TestCase):
    """
    Test cases for Celery tasks
    """

    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="test@gmail.com",
        )
        self.order = Order.objects.create(
            user=self.user,
            product_name="TestProduct",
            price=10
        )

        # Create a temporary image and upload to MEDIA_ROOT
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        temp_image = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image = Image.new("RGB", (800, 800), color="red")
        image.save(temp_image.name)
        temp_image.seek(0)

        uploaded_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=open(temp_image.name, "rb").read(),
            content_type="image/jpeg"
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            image=uploaded_image
        )

        self.created_files = [self.user_profile.image.path]
        temp_image.close()
        os.unlink(temp_image.name)

    def tearDown(self):
        """
        Remove only images created during test cases.
        """
        for file_path in self.created_files:
            if os.path.exists(file_path):
                os.remove(file_path)
            # Remove resized versions if they exist
            sizes = ['thumbnail', 'medium', 'large']
            for size in sizes:
                resized_path = os.path.join(
                    os.path.dirname(os.path.dirname(file_path)), size,
                    os.path.basename(file_path)
                )
                if os.path.exists(resized_path):
                    os.remove(resized_path)

    def test_send_welcome_email_success(self):
        """
        Test successful welcome email sending
        """

        send_welcome_email(self.user.email, self.user.username)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to Our Platform!")
        self.assertEqual(mail.outbox[0].from_email, "ashfaq319535@gmail.com")

    @patch('celery_app.tasks.send_mail', side_effect=Exception("SMTP Error"))
    def test_send_welcome_email_retry_on_failure(self, mock_send_mail):
        """
        Test that the task retries when send_mail raises an exception.
        """

        with self.assertRaises(Exception):
            send_welcome_email(self.user.email, self.user.username)

        mock_send_mail.assert_called_once()

    def test_generate_and_email_invoice_success(self):
        """
        Test successful invoice generation and email
        """

        send_invoice_email(self.order.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "ashfaq319535@gmail.com")
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        self.assertEqual(len(mail.outbox[0].attachments), 1)

    @patch('celery_app.tasks.EmailMessage.send', side_effect=Exception("SMTP Error"))
    def test_send_invoice_email_retry_on_failure(self, mock_email_send):
        """
        Test that the task retries when EmailMessage.send() raises an exception.
        """
        with self.assertRaises(Exception):
            send_invoice_email(self.order.id)

        mock_email_send.assert_called_once()

    def test_send_daily_summary_emails(self):
        """
        Test daily summary email sending
        """

        send_daily_summary_emails()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject, "Your Daily Activity")

    @patch('celery_app.tasks.send_mail', side_effect=Exception("SMTP Error"))
    def test_send_daily_summary_emails_failure(self, mock_send_mail):
        """
        Task should propagate exception if send_mail fails for any user.
        """
        with self.assertRaises(Exception):
            send_daily_summary_emails()

        mock_send_mail.assert_called()

    def test_process_image_creates_resized_versions(self):
        """
        Test that process_image creates all resized versions correctly.
        """
        result = process_image(self.user_profile.id)
        self.assertIn("Successfully processed image", result)

        # Check if resized images exist
        sizes = ['thumbnail', 'medium', 'large']
        for size in sizes:
            resize_dir = os.path.join(
                os.path.dirname(os.path.dirname(self.user_profile.image.path)), size
            )
            resized_path = os.path.join(resize_dir, os.path.basename(self.user_profile.image.path))
            self.assertTrue(os.path.exists(resized_path), f"{size} image not found")

    @patch('celery_app.tasks.Image.open', side_effect=Exception("File Error"))
    def test_process_image_retry_on_failure(self, mock_image_open):
        """
        Test that the task retries when Image.open fails.
        """
        with self.assertRaises(Exception):
            process_image(self.user_profile.id)

        mock_image_open.assert_called_once()
