from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class User(AbstractUser):
    class Types(models.TextChoices):
        BUYER = 'BUYER', 'Buyer'
        FARMER = 'FARMER', 'Farmer'

    base_type = Types.BUYER

    email = models.EmailField(unique=True)

    user_type = models.CharField(
        max_length=50,
        choices=Types.choices,
        default=base_type
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        default='',
        validators=[
            RegexValidator(
                r'^\+?\d{9,15}$',
                message="Enter a valid phone number."
            )
        ],
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="api_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="api_user_permissions_set",
        related_query_name="user",
    )

    USERNAME_FIELD = 'username'  # Keep username login
    REQUIRED_FIELDS = ['email', 'user_type', 'phone_number', 'location']

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Animal(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='animals_for_sale',
        limit_choices_to={'user_type': User.Types.FARMER}
    )

    name = models.CharField(max_length=100, help_text="A display name for the animal or group of animals.")

    class AnimalTypes(models.TextChoices):
        COW = 'COW', 'Cow'
        GOAT = 'GOAT', 'Goat'
        SHEEP = 'SHEEP', 'Sheep'
        CHICKEN = 'CHICKEN', 'Chicken'
        PIG = 'PIG', 'Pig'

    animal_type = models.CharField(max_length=50, choices=AnimalTypes.choices)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField(help_text="Age in months")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='animal_images/', blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.breed} {self.get_animal_type_display()} - {self.farmer.username}"

class Order(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'user_type': User.Types.BUYER}
    )

    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid'

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'animal')

    def clean(self):
        if self.order.buyer == self.animal.farmer:
            raise ValidationError("A farmer cannot order their own animal.")

    def __str__(self):
        return f"{self.quantity} of {self.animal.name} in Order {self.order.id}"