from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_welcome_email, send_invoice_email, process_image
from .models import Order, UserProfile


@receiver(post_save, sender=User)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    if created:
        send_welcome_email.delay(instance.email, instance.username)


@receiver(post_save, sender=Order)
def send_invoice_on_order_creation(sender, instance, created, **kwargs):
    if created:
        send_invoice_email.delay(instance.id)


@receiver(post_save, sender=UserProfile)
def trigger_image_processing(sender, instance, created, **kwargs):
    if instance.image and created:
        process_image.delay(instance.id)
