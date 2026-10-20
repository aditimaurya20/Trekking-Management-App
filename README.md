# Trekking Management App

A role-based web application to manage trekking activities for organizers, staff, and participants. It replaces spreadsheets and phone coordination with one system for trek approvals, bookings, and slot tracking. Built as the final project for the MAD 1 course.

## Features

**Admin**
- Add, edit, and delete treks
- Add staff and manage them (blacklist, activate, delete)
- View and manage all users (blacklist or activate)
- View all bookings

**Staff**
- Dashboard of assigned treks
- View trek details and update trek status
- View the list of participants for each trek

**Trekker (User)**
- Register, log in, and edit profile
- Browse open treks and book a slot
- View and cancel own bookings

**General**
- Role-based access control (admin, staff, trekker)
- Overbooking prevention through available-slot tracking
- Custom IDs per role and booking, such as `A10001` and `B10001`
- Trek lifecycle: Pending, Approved, Open, Closed, Completed

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy |
| Database | SQLite |
| Frontend | HTML, Jinja2, Bootstrap |

## Project Structure

```
Trekking-Management-App/
├── app.py              # App entry point
├── routes.py           # All routes (auth, admin, staff, user)
├── models.py           # Database models (User, Trek, Booking, StaffProfile)
├── config.py           # App configuration
├── admin.py            # Script to create the default admin
├── requirements.txt
└── templates/          # Jinja2 templates (admin, staff, user, auth)
```

## Getting Started

**1. Clone the repo**

```bash
git clone https://github.com/aditimaurya20/Trekking-Management-App.git
cd Trekking-Management-App
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create the default admin**

```bash
python admin.py
```

**4. Run the app**

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser. The database file is created automatically on the first run.

## Demo Admin Login

- Email: `admin@trekking.com`
- Password: `admin123`

This is for demo purposes only.
