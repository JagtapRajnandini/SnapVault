# SnapVault

An OCR-powered document management web application that automatically extracts text from uploaded images and classifies them into categories.

## Overview

SnapVault allows users to upload screenshots and document images (bills, medical reports, certificates, etc.). The system automatically extracts text using OCR, classifies each document into one of 9 predefined categories using keyword-based scoring, and organizes everything in a searchable, filterable dashboard.

**Processing flow:**
Upload → Extension validation → SHA-256 duplicate detection → UUID file storage → Pillow image verification → OCR text extraction → Keyword-based classification → Database record → Dashboard/Search

## Features

- **User Authentication** — Registration, login, logout, and profile management with secure password hashing
- **Document Upload** — Image upload with multi-layer validation (extension check, Pillow verification, file size limit)
- **Duplicate Detection** — SHA-256 hash comparison prevents the same file from being uploaded twice
- **UUID File Storage** — Uploaded files are renamed to random UUIDs, preventing filename collisions and path traversal
- **OCR Text Extraction** — EasyOCR extracts readable text from uploaded images; failures are handled gracefully without crashing the upload
- **Automatic Classification** — Documents are classified into 9 categories (Bills, Medical, Education, Finance, Travel, Food, Shopping, Certificates, Miscellaneous) using keyword frequency scoring against OCR-extracted text
- **Dashboard** — Displays total document count, per-category counts (via SQL GROUP BY), and the 5 most recent uploads
- **Document History** — Paginated list of all uploaded documents with search and category filter
- **Search** — Full-text search across filename, OCR text, and category using SQL ILIKE queries
- **Category Filter** — Dropdown filter on the history page to show documents from a specific category
- **Document Detail View** — Shows image preview, metadata (filename, category, OCR status, file size, upload date), and the full extracted text
- **Reminders** — Create, view, complete, and delete reminders with optional linking to uploaded documents; overdue reminders are highlighted
- **Document Deletion** — POST-only deletion with CSRF protection and a confirmation modal
- **Secure File Serving** — Uploaded images are served through an authenticated route with ownership verification, not directly from a public static folder
- **CSRF Protection** — Flask-WTF CSRFProtect applied globally; all state-changing actions use CSRF tokens
- **IDOR Prevention** — Every database query that accesses a document or reminder includes `user_id == current_user.id` filtering
- **POST-only Logout** — Logout requires a POST request with a CSRF token, preventing logout-via-GET attacks
- **Open Redirect Protection** — The login `next` parameter is validated to reject external URLs
- **Custom Error Pages** — Styled 404 and 500 error pages

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| Flask | Web framework |
| SQLAlchemy | ORM and database queries |
| SQLite | Database (via `instance/app.db`) |
| Flask-Login | Session-based authentication |
| Flask-WTF | Form handling and CSRF protection |
| Flask-Bcrypt | Password hashing (bcrypt) |
| EasyOCR | Optical Character Recognition |
| Pillow | Image validation |
| Jinja2 | HTML templating |
| Bootstrap 5 | Frontend CSS framework (CDN) |
| python-dotenv | Environment variable management |

## Architecture

```
Screenshot Logger/
├── SnapVault/                      # Application package
│   ├── __init__.py                 # App factory, extensions, error handlers, route imports
│   ├── config.py                   # Configuration (SECRET_KEY, DB URI, UPLOAD_FOLDER)
│   ├── models/
│   │   ├── user.py                 # User model with password hashing
│   │   ├── document.py             # Document model with OCR fields
│   │   └── reminder.py             # Reminder model with document linking
│   ├── routes/
│   │   ├── auth_routes.py          # Register, login, logout, profile
│   │   ├── document_routes.py      # Upload, history, detail, delete, file serving
│   │   ├── dashboard_routes.py     # Dashboard with aggregation queries
│   │   └── reminder_routes.py      # Reminder CRUD
│   ├── forms/
│   │   ├── auth_forms.py           # RegisterForm, LoginForm
│   │   ├── document_forms.py       # UploadForm
│   │   └── reminder_forms.py       # ReminderForm
│   ├── services/
│   │   ├── storage_service.py      # File save, delete, hash, extension check, Pillow verify
│   │   ├── ocr_service.py          # EasyOCR text extraction
│   │   └── classification_service.py  # Keyword-based document classification
│   ├── utils/
│   │   └── constants.py            # Categories, keywords, allowed extensions, file size limit
│   ├── templates/                  # Jinja2 HTML templates
│   └── static/                     # CSS and JavaScript
├── uploads/                        # User file storage (gitignored)
├── instance/                       # SQLite database (gitignored)
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
└── .gitignore                      # Git exclusion rules
```

**Module responsibilities:**

- **routes/** — HTTP request handling. Each route validates input, delegates to services, and renders templates.
- **models/** — SQLAlchemy database models defining the schema and relationships.
- **forms/** — Flask-WTF form classes with validation rules.
- **services/** — Business logic (file I/O, OCR, classification). Routes never touch the filesystem directly.
- **utils/** — Application constants shared across modules.

## Application Flow

```
User uploads an image
        │
        ▼
Form validation (FileRequired + FileAllowed)
        │
        ▼
Extension check (allowed_extension)
        │
        ▼
SHA-256 hash computed (duplicate detection)
        │
        ▼
UUID-based filename generated
        │
        ▼
File saved to uploads/<user_id>/
        │
        ▼
Pillow verifies the file is a real image
        │
        ▼
Document row created (ocr_status = 'pending')
        │
        ▼
EasyOCR extracts text from the image
        │
        ▼
Keyword scoring classifies the document
        │
        ▼
Database updated (ocr_text, ocr_status, category)
        │
        ▼
User redirected to the document detail page
```

## Database Design

### User

Stores registered user accounts.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| username | String(50) | Unique, required |
| email | String(150) | Unique, required |
| password_hash | String(128) | Bcrypt hash (set via property) |
| created_at | DateTime | Auto-set on creation |
| updated_at | DateTime | Auto-set on creation and update |

**Relationships:** One User has many Documents and many Reminders (cascade delete).

### Document

Stores metadata and OCR results for each uploaded image.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | FK → User, cascade delete |
| original_filename | String(255) | Display name |
| stored_filename | String(255) | UUID-based name on disk, unique |
| file_size | Integer | Size in bytes |
| file_hash | String(64) | SHA-256 hex digest |
| file_path | String(500) | Relative path: `<user_id>/<stored_filename>` |
| ocr_text | Text | Extracted text (nullable) |
| ocr_status | String(20) | `pending`, `success`, or `failed` |
| category | String(50) | Classification result (default: Miscellaneous) |
| uploaded_at | DateTime | Auto-set on creation |

**Index:** Composite index on `(user_id, category)` for dashboard GROUP BY queries.
**Relationships:** One Document has many Reminders (SET NULL on delete).

### Reminder

Stores user-created reminders, optionally linked to a document.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | FK → User, cascade delete |
| document_id | Integer | FK → Document, nullable, SET NULL on delete |
| title | String(200) | Reminder description |
| due_date | Date | When the reminder is due |
| status | String(20) | `pending` or `completed` |
| created_at | DateTime | Auto-set on creation |

## Security

| Mechanism | Implementation |
|---|---|
| Password hashing | Flask-Bcrypt with a property setter on the User model |
| Session authentication | Flask-Login with `@login_required` on all protected routes |
| CSRF protection | Flask-WTF `CSRFProtect` applied globally; tokens embedded in all forms |
| IDOR prevention | Every query filters by `user_id == current_user.id` |
| Secure filenames | `werkzeug.secure_filename()` strips path traversal characters |
| UUID storage names | Uploaded files are renamed to `uuid4().hex` — original names are never used on disk |
| Authenticated file serving | Images served via a route that checks ownership, not from a public directory |
| POST-only destructive actions | Logout, delete, and reminder mutations require POST with CSRF tokens |
| Open redirect prevention | Login `next` parameter validated with `urlparse` to reject external URLs |
| Image verification | Pillow `verify()` confirms uploaded files are real images, not renamed executables |
| Duplicate detection | SHA-256 hash comparison before saving prevents identical re-uploads |
| SQLite FK enforcement | `PRAGMA foreign_keys=ON` set on every connection via SQLAlchemy event listener |

## OCR and Classification

**OCR:** EasyOCR (English, CPU mode). The Reader is instantiated once at module import and reused across all requests. `extract_text()` returns the joined text strings from all detections, or an empty string on failure. OCR failures do not crash the upload — the document is saved with `ocr_status = 'failed'`.

**Classification:** Keyword frequency scoring. The OCR text is lowercased and checked against keyword lists defined in `constants.py` for each of the 9 categories. The category with the highest match count wins. If no keywords match, the document is classified as "Miscellaneous". This is a rule-based system, not machine learning.

**Categories:** Bills, Medical, Education, Finance, Travel, Food, Shopping, Certificates, Miscellaneous.

## Search

The history page supports two filtering mechanisms:

- **Text search** (`?q=`): SQL `ILIKE` query across `original_filename`, `ocr_text`, and `category` columns.
- **Category filter** (`?category=`): Exact match on the `category` column.

Both filters can be combined. Results are ordered by upload date (newest first).

## Dashboard

The dashboard displays:

- **Total document count** — `SELECT COUNT(id) FROM document WHERE user_id = ?`
- **Per-category counts** — `GROUP BY category` aggregate query, displayed for all 9 categories
- **Recent uploads** — The 5 most recently uploaded documents

All counting is performed in the database using aggregate functions, not in Python.

## Installation

### Clone the repository

```bash
git clone https://github.com/JagtapRajnandini/SnapVault.git
cd SnapVault
```

### Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URI=sqlite:///app.db
FLASK_DEBUG=True
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Run the application

```bash
python run.py
```

Open your browser and visit `http://127.0.0.1:5000`.

Note: The first request that triggers OCR will take a few seconds while EasyOCR loads the model into memory.

## Usage

1. **Register** an account at `/register`
2. **Login** with your credentials
3. **Upload** a document image (PNG, JPG, or JPEG) from the Upload page
4. The system **extracts text** via OCR and **classifies** the document automatically
5. View the **document detail** page to see the extracted text and assigned category
6. Browse all documents in **Document History** with search and category filtering
7. Check the **Dashboard** for upload statistics and recent documents
8. **Set reminders** on important documents (bills, renewals, deadlines)
9. **Mark reminders** as complete or delete them from the Reminders page

## Routes

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | `/` | Home page (redirects to dashboard if logged in) | No |
| GET, POST | `/register` | User registration | No |
| GET, POST | `/login` | User login | No |
| POST | `/logout` | User logout | Yes |
| GET | `/profile` | User profile | Yes |
| GET | `/dashboard` | Dashboard with statistics | Yes |
| GET, POST | `/upload` | Document upload | Yes |
| GET | `/history` | Document list with search/filter | Yes |
| GET | `/document/<id>` | Document detail view | Yes |
| POST | `/document/<id>/delete` | Delete a document | Yes |
| GET | `/uploads/<user_id>/<filename>` | Serve uploaded image | Yes |
| GET | `/reminders` | List all reminders | Yes |
| GET, POST | `/reminders/create` | Create a new reminder | Yes |
| POST | `/reminders/<id>/complete` | Mark reminder as completed | Yes |
| POST | `/reminders/<id>/delete` | Delete a reminder | Yes |

## Project Status

This is a functional MVP built as a portfolio project. All core features (authentication, upload, OCR, classification, dashboard, search, reminders, security) are implemented and working. The application uses synchronous OCR processing, which is suitable for single-user or low-traffic usage but would require a task queue (e.g., Celery) for production-scale deployment.

## Future Improvements

- Asynchronous OCR processing with Celery and Redis
- PostgreSQL database for production deployment
- ML-based document classification to replace keyword scoring
- PDF upload support
- Bulk upload and batch processing
- Email or push notification reminders
- User account settings and password change

## Author

**Rajnandini Jagtap**
GitHub: [https://github.com/JagtapRajnandini](https://github.com/JagtapRajnandini)

## License

This project is intended for educational and portfolio purposes.
