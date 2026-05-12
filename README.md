# Holistic Map

Holistic Map is a Django web app for matching employees to internal roles based on:

- Skills + years of experience
- Education requirements
- Weighted match scoring (required criteria weighted more than preferred)

Built for executives, employers, and employees to collaborate on role definition and candidate fit inside a company.

Can be acessed via: http://136.112.20.152/

---

## Features

- **Role-based accounts**
  - Executive
  - Employer
  - Employee

- **Company management**
  - Executives create companies
  - Company-level secrets for employer/employee signup

- **Employee profiles**
  - Add/remove skills with years of experience
  - Add/remove education entries

- **Role creation**
  - Employers/Executives create roles
  - Add required/preferred skills one at a time
  - Add required/preferred education one at a time

- **Match analysis**
  - Weighted score by role fit
  - Required and preferred gap breakdown
  - Detailed role-to-employee match view

---

## Tech Stack

- **Backend:** Django
- **Database:** SQLite (local dev), PostgreSQL (production/Supabase)
- **Server:** Gunicorn + nginx (VM deployment)
- **Static files:** HTML/CSS/JS

---

## Project Structure

```text
.
├── config/                  # Django project settings/urls/wsgi
├── holisticmap/             # Main app (models, views, templates, services)
├── deploy/                  # VM deployment templates/docs (systemd, nginx, env)
├── requirements.txt
└── manage.py
