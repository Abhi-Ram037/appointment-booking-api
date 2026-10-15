from datetime import date, datetime, time, timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Customer, ServiceProvider, Appointment
from .serializers import (
    CustomerSerializer,
    ServiceProviderSerializer,
    AppointmentSerializer,
)


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class ServiceProviderListCreateView(generics.ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            'customer', 'service_provider'
        ).all()

        date = self.request.query_params.get('date')
        provider = self.request.query_params.get('provider')
        appointment_status = self.request.query_params.get('status')

        if date:
            queryset = queryset.filter(appointment_date=date)

        if provider:
            if not provider.isdigit():
                raise ValidationError({
                    'provider': 'Provider must be a valid numeric ID.'
                })
            queryset = queryset.filter(service_provider_id=provider)

        if appointment_status:
            valid_statuses = [
                choice[0] for choice in Appointment.STATUS_CHOICES
            ]
            if appointment_status not in valid_statuses:
                raise ValidationError({
                    'status': 'Invalid appointment status.'
                })
            queryset = queryset.filter(status=appointment_status)

        return queryset

    def perform_create(self, serializer):
        serializer.save(status='Pending')



class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.select_related(
        'customer', 'service_provider'
    )
    serializer_class = AppointmentSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'Cancelled':
            return Response(
                {'error': 'Cancelled appointments cannot be changed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



class AppointmentUpdateView(generics.UpdateAPIView):
    queryset = Appointment.objects.select_related(
        'customer', 'service_provider'
    )
    serializer_class = AppointmentSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'Cancelled':
            return Response(
                {'error': 'Cancelled appointments cannot be changed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class AppointmentStatusUpdateView(APIView):
    def put(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        valid_statuses = [
            choice[0] for choice in Appointment.STATUS_CHOICES
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    'error': 'Status must be Pending, Confirmed, '
                             'Completed, or Cancelled.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if appointment.status == 'Cancelled':
            return Response(
                {'error': 'Cancelled appointments cannot be changed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = new_status
        appointment.save(update_fields=['status'])

        return Response({
            'message': 'Appointment status updated successfully.',
            'id': appointment.id,
            'status': appointment.status
        })

    
class ProviderAvailabilityView(APIView):
    def get(self, request, pk):
        try:
            provider = ServiceProvider.objects.get(pk=pk)
        except ServiceProvider.DoesNotExist:
            return Response(
                {'error': 'Service provider not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        selected_date = request.query_params.get('date')

        if not selected_date:
            return Response(
                {'error': 'Please provide a date in YYYY-MM-DD format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointments = Appointment.objects.filter(
            service_provider=provider,
            appointment_date=selected_date
        ).exclude(status='Cancelled').order_by('start_time')

        booked_slots = []
        for appointment in appointments:
            booked_slots.append({
                'appointment_id': appointment.id,
                'start_time': appointment.start_time.strftime('%H:%M'),
                'end_time': appointment.end_time.strftime('%H:%M'),
                'status': appointment.status
            })

        available_slots = []
        current_time = time(9, 0)
        closing_time = time(17, 0)

        while (
            datetime.combine(selected_date, current_time)
            + timedelta(minutes=30)
        ).time() <= closing_time:
            slot_end = (
                datetime.combine(selected_date, current_time)
                + timedelta(minutes=30)
            ).time()

            conflict = appointments.filter(
                start_time__lt=slot_end,
                end_time__gt=current_time
            ).exists()

            if not conflict:
                available_slots.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M')
                })

            current_time = slot_end

        return Response({
            'provider_id': provider.id,
            'provider_name': provider.name,
            'date': selected_date.isoformat(),
            'working_hours': '09:00-17:00',
            'available_slots': available_slots,
            'booked_slots': booked_slots
        })


class CancelAppointmentView(APIView):
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if appointment.status == 'Cancelled':
            return Response(
                {'error': 'Appointment is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if appointment.status == 'Completed':
            return Response(
                {'error': 'Completed appointments cannot be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'Cancelled'
        appointment.save(update_fields=['status'])

        return Response({
            'message': 'Appointment cancelled successfully.',
            'appointment_id': appointment.id,
            'status': appointment.status
        }, status=status.HTTP_200_OK)

