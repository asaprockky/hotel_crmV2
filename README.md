Hotel CRM/POS System
A Django-based Hotel CRM and Point of Sale (POS) system designed for hotel owners in Uzbekistan to streamline reservation management, enhance guest experiences. This system offers features such as dynamic room availability checks, Telegram notifications, and a modern, responsive reservation interface.
Features

Reservation Management: Create and manage room reservations with an intuitive form, ensuring rooms are only available for unreserved dates.
Room Availability Checks: Automatically filters out rooms reserved for overlapping date ranges using Django querysets.
Modern UI: A styled reservation page with a dark navy theme (#030D28), gold accents (#CDA274), and Montserrat font, built with Bootstrap 5.3 and Crispy Forms.
Dynamic Room Selection: AJAX-driven room dropdown updates to show only available rooms based on selected check-in and check-out dates.
Telegram Notifications: Real-time alerts for staff about new reservations or updates (planned for Booking.com integration).
Booking.com Integration (Planned): Support for syncing reservations and availability with Booking.com via API or email parsing.
Responsive Design: Optimized for iPad and laptops, ensuring usability for hotel staff on the go.

Project Structure
hotel-crm/
├── hotel_crm/
│   ├── settings.py
│   ├── urls.py
├── reservations/
│   ├── static/
│   │   ├── css/
│   │   │   └── reservation_form.css
│   ├── templates/
│   │   ├── buttons_funcs/
│   │   │   └── create_reservation_form.html
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
├── manage.py
├── README.md
├── requirements.txt


reservations/: Main app containing models, views, forms, templates, and static files.
templates/buttons_funcs/: HTML templates for the reservation interface.
static/css/: CSS styles for the reservation page.
models.py: Defines Room and Reservation models for managing hotel data.
forms.py: Includes CreateReservationForm for dynamic room selection.
views.py: Handles reservation creation and AJAX room availability checks.

Prerequisites

Python 3.8+
Django 4.2+
PostgreSQL (recommended) or SQLite
Node.js (optional, for development tools)
Booking.com Connectivity Partner account (for API integration)

Installation

Clone the Repository:
git clone https://github.com/your-username/hotel-crm.git
cd hotel-crm


Set Up a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure Environment Variables:

Create a .env file in the project root:touch .env


Add the following (replace values as needed):SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TELEGRAM_BOT_TOKEN=your-telegram-bot-token




Apply Migrations:
python manage.py makemigrations
python manage.py migrate


Collect Static Files:
python manage.py collectstatic


Create a Superuser:
python manage.py createsuperuser


Run the Development Server:
python manage.py runserver


Access the app at http://localhost:8000/reservation/create/.



Usage

Create a Reservation:

Navigate to /reservation/create/ to access the reservation form.
Select check-in and check-out dates to dynamically filter available rooms.
Submit the form to create a reservation, ensuring no double bookings occur.


Room Availability:

The system checks for overlapping reservations using the get_available_rooms function, ensuring rooms are unavailable for reserved dates.


Booking.com Integration (Planned):

Enable email notifications in Booking.com’s Extranet (Account > Notification settings) to receive reservation alerts.
Parse emails or integrate with Booking.com’s API to sync bookings with your Reservation model.


Telegram Notifications:

Configure your Telegram bot token in .env to enable real-time staff alerts for new reservations.



Development
Models

Room: Represents a hotel room with fields like name and hotel (ForeignKey).
Reservation: Stores booking details with check_in, check_out, room, and deposit_amount.

Key Views

CreateReservationView: Handles reservation form rendering and submission.
get_available_rooms_view: AJAX endpoint to fetch available rooms based on date ranges.

Forms

CreateReservationForm: Dynamically filters rooms based on availability using get_available_rooms.

Static Files

reservation_form.css: Styles the reservation page with a dark navy theme and gold accents.
create_reservation_form.html: Template for the reservation interface, using Bootstrap 5.3 and Crispy Forms.

Adding Features

Booking.com API: Apply for Connectivity Partner status at connect.booking.com and implement API calls for reservation syncing.
Email Parsing: Use Python’s imaplib to parse Booking.com emails and create Reservation entries.
Multi-Hotel Support: Extend the Hotel model to support multiple properties per user.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

Testing

Unit Tests: Add tests for get_available_rooms and form validation in reservations/tests.py.
Manual Testing:
Create reservations with overlapping dates to verify availability logic.
Test responsive design on iPad and mobile devices.
Simulate Booking.com emails to test parsing logic.



License
This project is licensed under the MIT License. See LICENSE for details.
Contact
For support or inquiries, contact:

Email: lukejohnes27@gmail.com
Telegram: @s17aj_04

