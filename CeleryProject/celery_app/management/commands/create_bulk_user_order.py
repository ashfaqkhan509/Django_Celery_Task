from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from celery_app.models import UserProfile, Order
from django.db import transaction
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = "Create users with profiles and orders in bulk"

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--orders', type=int, default=5, help='Number of orders per user')

    @transaction.atomic
    def handle(self, *args, **options):
        num_users = options['users']
        num_orders = options['orders']

        self.stdout.write(self.style.WARNING(f"Creating {num_users} users with {num_orders} orders each..."))

        users = []
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            user = User(username=username, email=email)
            user.set_password("test123")
            users.append(user)

        # Bulk create users
        created_users = User.objects.bulk_create(users)

        # Create UserProfiles
        profiles = [UserProfile(user=user, image='profile_images/default.png') for user in created_users]
        UserProfile.objects.bulk_create(profiles)

        # Create Orders
        orders = []
        for user in created_users:
            for _ in range(num_orders):
                orders.append(Order(
                    user=user,
                    product_name=fake.word(),
                    price=round(random.uniform(10, 500), 2)
                ))
        Order.objects.bulk_create(orders)

        self.stdout.write(self.style.SUCCESS("Bulk users, profiles, and orders created successfully!"))
