
from django.urls import path

from .views import (
    CustomerListCreateView,
    ServiceProviderListCreateView,
    AppointmentListCreateView,
    AppointmentDetailView,
    AppointmentStatusUpdateView,
    ProviderAvailabilityView,
    CancelAppointmentView,
)

urlpatterns = [
    # Customer APIs
    path(
        'customers/',
        CustomerListCreateView.as_view(),
        name='customer-list'
    ),

    # Service Provider APIs
    path(
        'providers/',
        ServiceProviderListCreateView.as_view(),
        name='provider-list'
    ),

    # Appointment booking and filtering
    path(
        'appointments/',
        AppointmentListCreateView.as_view(),
        name='appointment-list-create'
    ),

    # Get appointment details and reschedule
    path(
        'appointments/<int:pk>/',
        AppointmentDetailView.as_view(),
        name='appointment-detail-update'
    ),

    # Update appointment status
    path(
        'appointments/<int:pk>/status/',
        AppointmentStatusUpdateView.as_view(),
        name='appointment-status-update'
    ),

    # Get provider availability
    path(
        'providers/<int:pk>/availability/',
        ProviderAvailabilityView.as_view(),
        name='provider-availability'
    ),

    # Cancel appointment
    path(
        'appointments/<int:pk>/cancel/',
        CancelAppointmentView.as_view(),
        name='cancel-appointment'
    ),
]
