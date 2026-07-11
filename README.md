# SnapVault

SnapVault is a Flask-based web application for securely organizing and managing personal documents. It provides user authentication, document management, reminders, and a structured backend architecture designed for future scalability and additional intelligent features.

## Features

### Authentication

* User registration
* User login and logout
* Secure password hashing using Flask-Bcrypt
* Session management with Flask-Login
* Protected routes for authenticated users

### Database

* SQLAlchemy ORM
* SQLite database
* Relational data models
* Automatic database initialization

### Forms & Validation

* Flask-WTF forms
* Server-side validation
* CSRF protection
* Custom validation for duplicate usernames and email addresses

### User Interface

* Responsive Bootstrap 5 layout
* Reusable base template
* Home page
* Registration page
* Login page
* Profile page
* Dashboard placeholder

## Tech Stack

* Python
* Flask
* Flask-SQLAlchemy
* Flask-WTF
* Flask-Login
* Flask-Bcrypt
* SQLite
* Jinja2
* Bootstrap 5

## Project Structure

```text
SnapVault/
├── forms/
├── models/
├── routes/
├── services/
├── static/
├── templates/
├── utils/
├── config.py
└── __init__.py
```

## Available Routes

| Route        | Description            |
| ------------ | ---------------------- |
| `/`          | Home page              |
| `/register`  | Register a new account |
| `/login`     | User login             |
| `/logout`    | User logout            |
| `/profile`   | User profile           |
| `/dashboard` | Dashboard              |

## Planned Features

* Document upload and storage
* OCR-based text extraction
* Automatic document categorization
* Full-text document search
* Reminder management
* Dashboard analytics
* AI-assisted document organization

## Getting Started

### Clone the repository

```bash
git clone <repository-url>
cd SnapVault
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///app.db
```

### Run the application

```bash
python run.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## License

This project is intended for educational and portfolio purposes.
