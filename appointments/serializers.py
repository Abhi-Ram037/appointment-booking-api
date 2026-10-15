
from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Customer, ServiceProvider, Appointment


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source='customer.name', read_only=True
    )
    provider_name = serializers.CharField(
        source='service_provider.name', read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer',
            'customer_name',
            'service_provider',
            'provider_name',
            'appointment_date',
            'start_time',
            'end_time',
            'status',
            'reason',
        ]
        read_only_fields = ['id', 'status']

    def validate(self, data):
        instance = self.instance

        appointment_date = data.get(
            'appointment_date',
            instance.appointment_date if instance else None
        )
        start_time = data.get(
            'start_time',
            instance.start_time if instance else None
        )
        end_time = data.get(
            'end_time',
            instance.end_time if instance else None
        )
        provider = data.get(
            'service_provider',
            instance.service_provider if instance else None
        )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be later than start time.'
            })

        if appointment_date and start_time:
            appointment_datetime = timezone.make_aware(
                datetime.combine(appointment_date, start_time),
                timezone.get_current_timezone()
            )

            if appointment_datetime <= timezone.now():
                raise serializers.ValidationError({
                    'appointment_date':
                    'Appointments cannot be booked in the past.'
                })

        if appointment_date and start_time and end_time and provider:
            overlapping = Appointment.objects.filter(
                service_provider=provider,
                appointment_date=appointment_date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(status='Cancelled')

            if instance:
                overlapping = overlapping.exclude(pk=instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({
                    'time': 'This provider already has an appointment '
                            'during the selected time slot.'
                })

        return data
