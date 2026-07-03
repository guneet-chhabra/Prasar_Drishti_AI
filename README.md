# Prasar Drishti AI

AI/ML-based Sports Intelligence and News Analytics System using NewsOnAir data.

## Step 1: Login Authentication

This first slice adds two login roles:

- `admin / admin123`
- `user / user123`


### Run it locally

Terminal 1:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements-auth.txt
python run.py
```

Terminal 2:

```powershell
cd frontend
python -m http.server 3000
```

Open:

```text
http://localhost:3000
```

Important: keep the frontend and backend hostnames consistent. If you open the
frontend as `http://localhost:3000`, the frontend will call
`http://localhost:5000`. If you open it as `http://127.0.0.1:3000`, it will call
`http://127.0.0.1:5000`. Mixing `localhost` and `127.0.0.1` can make browser
session cookies disappear, which causes protected routes to return `401`.

The app also returns a signed login token and stores it in browser local storage
so protected routes keep working during local development even if cookies are
blocked or inconsistent.


