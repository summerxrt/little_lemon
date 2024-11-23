from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Category model for menu item classification
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title

# Menu item model for the restaurant's menu items
class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

# Cart model to hold items for a user before they place an order
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('menuitem', 'user')

    def __str__(self):
        return f"Cart of {self.user.username} with {self.menuitem.title}"

# Order model for storing user orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True,
        limit_choices_to={'groups__name': "Delivery crew"}
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

# Order item model for tracking items within each order
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menuitem.title} in order #{self.order.id}"

# Booking model for table reservations
from django.utils import timezone

class Booking(models.Model):
    customer_name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField()
    table_number = models.IntegerField(null=True)
    reservation_date = models.DateTimeField(default=timezone.now)
    reservation_slot = models.IntegerField(default=1)
    booking_date = models.DateTimeField(default=timezone.now)  # Automatically use the current date

    def __str__(self):
        return f"Booking for {self.customer_name} on {self.reservation_date}"


# Reservation model (if needed separately)
class Reservation(models.Model):
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    table_number = models.IntegerField()
    reservation_date = models.DateTimeField()

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.reservation_date}"

# Menu model for restaurant menu items
class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Booking(models.Model):
    customer_name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField()
    table_number = models.IntegerField(null=True)
    reservation_date = models.DateTimeField(default=timezone.now)
    reservation_slot = models.IntegerField(default=1)
    booking_date = models.DateTimeField(default=timezone.now)  # Automatically set to current time

    def __str__(self):
        return f"Booking for {self.customer_name} on {self.reservation_date}"