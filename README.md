# Freelancer Project

Simple Django freelance job platform.

## Requirements

- Python 3.10+ (recommended)
- pip
- virtualenv or `venv`

## Setup

1. Open a terminal in the project root:
   ```powershell
   cd c:\Users\mm\Desktop\check\freelancer
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Install dependencies from `requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```powershell
   python manage.py migrate
   ```

5. Create a superuser:
   ```powershell
   python manage.py createsuperuser
   ```

## Run locally

Start the app with Daphne:

```powershell
daphne freelancer.asgi:application
```

Then open in your browser:

```text
http://127.0.0.1:8000/
```

## Notes

- The project uses SQLite by default (`db.sqlite3`).
- `channels` and `daphne` are already included in `requirements.txt`.
- Keep `DEBUG = True` only for local development.
