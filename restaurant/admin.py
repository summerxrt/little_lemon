from django.contrib import admin
from .models import Menu, Booking

# Register the Menu model
admin.site.register(Menu)

# Customize the Booking model's admin interface
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'email', 'table_number', 'booking_date', 'reservation_date', 'reservation_slot')
    search_fields = ('customer_name', 'email')
    list_filter = ('booking_date', 'reservation_date', 'reservation_slot')
