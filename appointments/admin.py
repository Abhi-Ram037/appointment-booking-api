
from django.contrib import admin
from .models import Customer, ServiceProvider, Appointment


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    search_fields = ('name', 'email')


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'email')
    search_fields = ('name', 'specialization', 'email')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'service_provider',
        'appointment_date',
        'start_time',
        'end_time',
        'status',
    )
    list_filter = ('appointment_date', 'status', 'service_provider')
    search_fields = ('customer__name', 'service_provider__name')
