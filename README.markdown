# Hotel CRM/POS System

A Django-based Hotel CRM and Point of Sale (POS) system designed for hotel owners in Uzbekistan to streamline reservation management and enhance guest experiences. This system offers features such as dynamic room availability checks, Telegram notifications, and a modern, responsive reservation interface.
## 🚀 Demo

Check out the live demo: [Demo Link](https://fulstek.uz/hotel_crm/)
Username : testgithub
Password : FollowMe

## Features

- **Reservation Management**: Create and manage room reservations with an intuitive form, ensuring rooms are only available for unreserved dates.
- **Room Availability Checks**: Automatically filters out rooms reserved for overlapping date ranges using Django querysets.
- **Modern UI**: A styled reservation page with a dark navy theme (`#030D28`), gold accents (`#CDA274`), and Montserrat font, built with Bootstrap 5.3 and Crispy Forms.
- **Dynamic Room Selection**: AJAX-driven room dropdown updates to show only available rooms based on selected check-in and check-out dates.
- **Telegram Notifications**: Real-time alerts for staff about new reservations or updates.
- **Responsive Design**: Optimized for iPad and mobile devices, ensuring usability for hotel staff on the go.

## Project Structure

```
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
```

- **reservations/**: Main app containing models, views, forms, templates, and static files.
- **templates/buttons_funcs/**: HTML templates for the reservation interface.
- **static/css/**: CSS styles for the reservation page.
- **models.py**: Defines `Room` and `Reservation` models for managing hotel data.
- **forms.py**: Includes `CreateReservationForm` for dynamic room selection.
- **views.py**: Handles reservation creation and AJAX room availability checks.

## Prerequisites

- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite
- Node.js (optional, for development tools)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/hotel-crm.git
   cd hotel-crm
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:

   - Create a `.env` file in the project root:

     ```bash
     touch .env
     ```
   - Add the following (replace values as needed):

     ```env
     SECRET_KEY=your-django-secret-key
     DEBUG=True
     DATABASE_URL=sqlite:///db.sqlite3
     TELEGRAM_BOT_TOKEN=your-telegram-bot-token
     ```

5. **Apply Migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Collect Static Files**:

   ```bash
   python manage.py collectstatic
   ```

7. **Create a Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

   - Access the app at `http://localhost:8000/reservation/create/`.

## Usage

1. **Create a Reservation**:

   - Navigate to `/reservation/create/` to access the reservation form.
   - Select check-in and check-out dates to dynamically filter available rooms.
   - Submit the form to create a reservation, ensuring no double bookings occur.

2. **Room Availability**:

   - The system checks for overlapping reservations using the `get_available_rooms` function, ensuring rooms are unavailable for reserved dates.

3. **Telegram Notifications**:

   - Configure your Telegram bot token in `.env` to enable real-time staff alerts for new reservations.

## Development

### Models

- **Room**: Represents a hotel room with fields like `name` and `hotel` (ForeignKey).
- **Reservation**: Stores booking details with `check_in`, `check_out`, `room`, and `deposit_amount`.

### Key Views

- **CreateReservationView**: Handles reservation form rendering and submission.
- **get_available_rooms_view**: AJAX endpoint to fetch available rooms based on date ranges.

### Forms

- **CreateReservationForm**: Dynamically filters rooms based on availability using `get_available_rooms`.

### Static Files

- **reservation_form.css**: Styles the reservation page with a dark navy theme and gold accents.
- **create_reservation_form.html**: Template for the reservation interface, using Bootstrap 5.3 and Crispy Forms.

### Adding Features

- **Email Notifications**: Implement email parsing for reservation confirmations using Python’s `imaplib`.
- **Multi-Hotel Support**: Extend the `Hotel` model to support multiple properties per user.
- **Payment Integration**: Add support for payment gateways like Stripe for deposit processing.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## Testing

- **Unit Tests**: Add tests for `get_available_rooms` and form validation in `reservations/tests.py`.
- **Manual Testing**:
  - Create reservations with overlapping dates to verify availability logic.
  - Test responsive design on iPad and mobile devices.
  - Simulate reservation creation to test Telegram notifications.

## License

This project is licensed under the MIT License. See LICENSE for details.

## Contact

For support or inquiries, contact:

- Email: lukejohnes27@gmail.com
- Telegram: @s17aj_04
