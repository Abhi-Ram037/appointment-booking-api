
from datetime import date, timedelta, time

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Customer, ServiceProvider, Appointment


class AppointmentAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.customer = Customer.objects.create(
            name="Rahul Kumar",
            email="rahul_test@example.com",
            phone="9876543210"
        )

        self.provider = ServiceProvider.objects.create(
            name="Dr. Priya",
            specialization="General Consultation",
            email="priya_test@example.com"
        )

        self.future_date = date.today() + timedelta(days=10)

        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service_provider=self.provider,
            appointment_date=self.future_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
            status="Pending",
            reason="General consultation"
        )

    def test_create_customer(self):
        response = self.client.post(
            "/customers/",
            {
                "name": "Suresh",
                "email": "suresh_test@example.com",
                "phone": "9123456780"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_create_provider(self):
        response = self.client.post(
            "/providers/",
            {
                "name": "Dr. Kumar",
                "specialization": "Dental",
                "email": "kumar_test@example.com"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_get_appointments(self):
        response = self.client.get("/appointments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_book_appointment(self):
        response = self.client.post(
            "/appointments/",
            {
                "customer": self.customer.id,
                "service_provider": self.provider.id,
                "appointment_date": str(self.future_date),
                "start_time": "12:00:00",
                "end_time": "13:00:00",
                "reason": "Follow-up consultation"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "Pending")

    def test_reject_overlapping_appointment(self):
        response = self.client.post(
            "/appointments/",
            {
                "customer": self.customer.id,
                "service_provider": self.provider.id,
                "appointment_date": str(self.future_date),
                "start_time": "10:30:00",
                "end_time": "11:30:00",
                "reason": "Another consultation"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_reschedule_appointment(self):
        new_date = self.future_date + timedelta(days=1)

        response = self.client.put(
            f"/appointments/{self.appointment.id}/",
            {
                "appointment_date": str(new_date),
                "start_time": "14:00:00",
                "end_time": "15:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.appointment_date, new_date)

    def test_cancel_appointment(self):
        response = self.client.post(
            f"/appointments/{self.appointment.id}/cancel/"
        )

        self.assertEqual(response.status_code, 200)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "Cancelled")

    def test_provider_availability(self):
        response = self.client.get(
            f"/providers/{self.provider.id}/availability/",
            {"date": str(self.future_date)}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["booked_slots"]), 1)

    def test_cancelled_appointment_cannot_be_rescheduled(self):
        self.appointment.status = "Cancelled"
        self.appointment.save()

        response = self.client.put(
            f"/appointments/{self.appointment.id}/",
            {
                "appointment_date": str(
                    self.future_date + timedelta(days=1)
                ),
                "start_time": "14:00:00",
                "end_time": "15:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
