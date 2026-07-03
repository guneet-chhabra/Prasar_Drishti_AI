# Prasar Drishti AI

AI/ML-based Sports Intelligence and News Analytics System using NewsOnAir data.

## Step 1: Login Authentication

This first slice adds two login roles:

- `admin / admin123`
- `user / user123`

### Files to study and code first

- `backend/run.py` starts the Flask API.
- `backend/app/__init__.py` creates the Flask app and registers API routes.
- `backend/api/auth.py` contains login, logout, current-user, and admin-only route logic.
- `backend/config.py` stores shared configuration.
- `frontend/index.html` is the login page.
- `frontend/styles/auth.css` applies the UI style from the supplied mockup.
- `frontend/app/auth.js` connects the login page to the Flask API.

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

## What to Build Next

1. Replace demo users with a real `users` database table.
2. Add a protected dashboard route for logged-in users.
3. Add admin-only controls for scraper status and model runs.
4. Connect the NewsOnAir scraper to store articles.
5. Build sentiment analysis APIs and charts.
6. Build Indian Sports Development Index APIs and charts.
7. Build FIFA prediction APIs and charts.

## Step 2: NewsOnAir Scraper

Install the scraper dependencies:

```powershell
cd backend
.\venv\Scripts\activate
python -m pip install -r requirements-scraper.txt
```

Run the scraper manually:

```powershell
python -m scraper.newsonair_scraper --categories sports national international business --limit 5
```

It saves:

- `backend/data/raw/newsonair_articles.json`
- `backend/data/raw/newsonair_articles.csv`

API routes:

- `GET /api/news/articles` shows saved scraped data for any logged-in user.
- `POST /api/news/scrape` runs a fresh scrape for admin users only.
- `POST /api/news/scrape-last-month` builds the initial archive from the last 30 days of news across government, sports, business, international, and miscellaneous categories.
- `POST /api/news/archive-today` merges today's file into the long-term archive.

Recommended data files:

- `backend/data/raw/today_YYYY-MM-DD.json`: today's rolling data.
- `backend/data/raw/archive_articles.json`: long-term historical sentiment corpus.
- `backend/data/raw/newsonair_articles.json`: older default/demo dataset.

Build the initial last-month dataset:

```powershell
python -m scraper.newsonair_scraper --days 30 --pages 35 --limit 300 --stem archive_articles
```

Update today's data once:

```powershell
python -m scraper.newsonair_scraper --today --pages 3 --limit 40
```

Run the half-hour monitor in a separate terminal:

```powershell
python scripts\run_news_monitor.py
```

The monitor updates today's file every 30 minutes. When the date changes, it
merges that finished day into `archive_articles.json` and starts writing to the
new day's `today_YYYY-MM-DD.json`.

Each article still has `is_government_related`, so later we can filter:

- government-related articles for political sentiment analysis
- sports articles for Indian sports forecasting
- FIFA/football articles for World Cup prediction features

## ML Model Plan

See `backend/ml/MODEL_PLAN.md`.

Short version:

- Start with TF-IDF + Logistic Regression and TF-IDF + Linear SVM.
- Compare with Naive Bayes, Random Forest, and XGBoost.
- Later test MLP, LSTM/BiLSTM, and DistilBERT.
- Use ReLU for simple dense networks, GELU for transformer models, Tanh/Sigmoid inside LSTM, and Softmax for the final 3-class output.
- Compare models using Accuracy, Macro F1-score, precision, recall, and confusion matrix.

## Dependency Note

Use `backend/requirements-auth.txt` for the login step. The full `backend/requirements.txt`
installs the ML stack and may fail on packages like `shap` depending on your Python version
and compiler setup. We will handle those packages later when we start model training.
