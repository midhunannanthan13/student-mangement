# Student Management System (Full-Stack)

Add, view, edit, delete and search students.

```
Browser -> Frontend (HTML + CSS + JS) -> fetch() -> Django REST API -> MySQL
           Live Server / Vercel                      laptop / Vercel     Workbench (local) / Aiven (online)
```

| Part      | Technology                     | Local                    | Online            |
|-----------|--------------------------------|--------------------------|-------------------|
| Frontend  | HTML, CSS, JavaScript          | VS Code Live Server      | Vercel            |
| Backend   | Django + Django REST Framework | `manage.py runserver`    | Vercel            |
| Database  | MySQL                          | MySQL Workbench / WAMP   | Aiven (free)      |

---

## 1. Run it on your computer

**Step 1: create the database in MySQL Workbench**

Open the connection *Local instance wampmysqld*, open a new SQL tab and run:

```sql
CREATE DATABASE student_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Copy `backend/.env.example` to `backend/.env` and fill in your local database settings.
If your Workbench password is different from the default, set it as `DB_PASSWORD` in that file.

**Step 2: backend** (Terminal 1)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py dbcheck       # shows which database you are connected to
python manage.py migrate       # creates the tables
python manage.py runserver
```

**Step 3: frontend**

Right-click `frontend/index.html` -> **Open with Live Server**
(address starts with `http://127.0.0.1:5500`). Add a student: you see the green message
**"Student added successfully."**

---

## 2. Use the free Aiven MySQL database (online)

1. Create a free **MySQL** service at https://console.aiven.io (no credit card).
2. On the service **Overview** page copy Host, Port, User, Password and Database name,
   and download the **CA certificate**.
3. Save the certificate as `backend/certs/aiven-ca.pem`.
4. Fill the five `DB_` lines in `backend/.env.aiven`, then (PowerShell, from `backend/`):

   ```powershell
   $env:ENV_FILE=".env.aiven"; python manage.py dbcheck; python manage.py migrate; Remove-Item Env:ENV_FILE
   ```

   `ENV_FILE` makes this ONE command use the Aiven file. Your normal `.env` stays local.

Free Aiven services power themselves off when unused. If the site shows a database error,
open the Aiven console and power the service on.

---

## 3. Deploy on Vercel

Create **two** Vercel projects from the same GitHub repository.

| Project  | Root Directory | Environment variables |
|----------|----------------|-----------------------|
| Backend  | `backend`      | `SECRET_KEY`, `DEBUG=False`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSL_CA=certs/aiven-ca.pem`, `CORS_ALLOWED_ORIGINS` |
| Frontend | `frontend`     | none |

Order that works:

1. Deploy the **backend** -> copy its address, e.g. `https://student-api.vercel.app`
2. In `frontend/app.js` set
   `PRODUCTION_API_URL = "https://student-api.vercel.app/api/students/"` -> commit and push.
3. Deploy the **frontend** -> copy its address, e.g. `https://student-web.vercel.app`
4. In the backend project add `CORS_ALLOWED_ORIGINS=https://student-web.vercel.app` -> **Redeploy**.

---

## API

| Action     | Method | URL                 |
|------------|--------|---------------------|
| Get all    | GET    | `/api/students/`    |
| Add        | POST   | `/api/students/`    |
| Get one    | GET    | `/api/students/1/`  |
| Update     | PUT    | `/api/students/1/`  |
| Delete     | DELETE | `/api/students/1/`  |

## Never upload to GitHub

`backend/.env`, `backend/.env.aiven` and `backend/venv/` (they hold passwords).
All three are already ignored by `backend/.gitignore`.
The Aiven CA certificate (`backend/certs/aiven-ca.pem`) is public and MUST be uploaded.
