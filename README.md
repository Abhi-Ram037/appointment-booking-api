\# Appointment Booking Management API



\## Project Overview



This project is a Django REST Framework API for managing appointments between customers and service providers. It uses SQLite3 as the database.



\## Technologies Used



\- Python

\- Django

\- Django REST Framework

\- SQLite3

\- Postman



\## Features



\- Customer management

\- Service provider management

\- Appointment booking

\- Appointment listing and filtering

\- Appointment rescheduling

\- Appointment status updates

\- Provider availability checking

\- Appointment cancellation

\- Validation for past bookings and overlapping appointments



\## API Endpoints



| Method | Endpoint | Description |

|---|---|---|

| POST | `/customers/` | Create customer |

| GET | `/customers/` | List customers |

| POST | `/providers/` | Create service provider |

| GET | `/providers/` | List providers |

| POST | `/appointments/` | Book appointment |

| GET | `/appointments/` | List appointments |

| GET | `/appointments/<id>/` | Get appointment details |

| PUT | `/appointments/<id>/` | Reschedule appointment |

| PUT | `/appointments/<id>/status/` | Update appointment status |

| GET | `/providers/<id>/availability/?date=YYYY-MM-DD` | Check availability |

| POST | `/appointments/<id>/cancel/` | Cancel appointment |



\## Setup Instructions



1\. Create and activate a Python virtual environment.

2\. Install dependencies using `python -m pip install -r requirements.txt`.

3\. Apply migrations using `python manage.py migrate`.

4\. Start the server using `python manage.py runserver`.

5\. Test the APIs using Postman or the Django REST Framework browsable API.



\## Database



SQLite3 stores customer, service provider, and appointment records.



\## Testing



API endpoints can be tested using Postman. Automated tests can be run with `python manage.py test appointments`.

