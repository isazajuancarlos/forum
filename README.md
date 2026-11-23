# Foro — Flask forum (code sample)

A small but complete discussion-forum web application built with **Python /
Flask**, kept as a public code sample. It demonstrates the pieces of a
public-facing, authenticated, database-backed web app.

## Stack

- **Flask** with a **Blueprint** for all routes
- **Flask-Login** for authentication and session management
  (`login_required`, `current_user`), with **Werkzeug** password hashing
- **Flask-WTF / WTForms** for form definition, validation and CSRF protection
- **Flask-Session** for server-side sessions
- **Jinja2** templates with inheritance (`base.html`) and macros (`macro.html`)
- **MySQL** persistence via **PyMySQL**
- WSGI deployment (`passenger_wsgi.py`)

## Structure (MVC)

| File | Role |
|------|------|
| `app.py` | Application factory: Flask app, config, extensions, blueprint |
| `ruta.py` | Routes (URL → controller), ~25 endpoints |
| `controlador.py` | Controllers: request handling, auth, business logic |
| `modelo.py` | Data access: MySQL connection + query helpers |
| `vista.py` | WTForms form classes |
| `config.py` | Flask configuration (random SECRET_KEY, session settings) |
| `templates/` | Jinja2 templates (forums, topics, messages, profile, auth) |
| `static/` | Static assets |

## Features

Registration and login, user profiles, categories, forums, topics and
messages — the usual forum CRUD, behind authentication, with validated forms
and server-rendered pages.

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your MySQL credentials
export $(grep -v '^#' .env | xargs)
python run.py                 # dev server at http://127.0.0.1:5000
```

Database credentials are read from environment variables (see `.env.example`);
nothing sensitive is committed to the repository.

## Note

An early personal project (2022–2023), published as a sample of Python/Flask
web development. The database schema is not included.
