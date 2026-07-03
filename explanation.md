# Prasar Drishti AI: Technical Architecture, Tech Stack, & Implementation Guide

**Prasar Drishti AI** is an AI/ML-powered Sports Intelligence and News Analytics System designed for Prasar Bharati (Akashwani Bhawan). The system harvests news broadcasts from the official NewsOnAir website, filters articles for relevance to the Indian Central Government, performs political stance classification, runs sports outcomes prediction models, and highlights India's medal prospects in upcoming world events.

---

## 1. Project Technology Stack

The project is built using a decoupled, performant, and lightweight technical stack:

### 1.1. Backend (Python 3)
* **Framework**: **Flask** (provides a RESTful API with routing, blueprints, CORS handling, and JWT-like authentication).
* **Scheduling**: **APScheduler** (schedules rolling daily scrapes and archives at 23:55 local time every night).
* **Web Scraping**: **BeautifulSoup4** & **Requests** (handles HTTP fetches, raw HTML document traversal, and structural DOM parsing).
* **Data Refreshers**: Exposes POST `/api/sports/refresh-indian-news` (invoking BeautifulSoup scraper categories for real-time news compilation) and POST `/api/sports/refresh-world-cup` (writing latest match outcomes to JSON file database).
* **NLP & Sentiment Analysis**: 
  * **NLTK (VADER)**: Tailored with a custom dictionary of political/developmental words to extract polarity features.
  * **scikit-learn**: Vectorizes content via TF-IDF (n-grams 1, 2) and runs a **Linear Support Vector Classifier (Linear SVC)** achieving **99.07% validation accuracy**.
* **Sports Predictor (FIFA Model)**:
  * **joblib**: Serializes and loads the trained Support Vector Machine sports model.
  * **pandas & numpy**: Parses rankings/schedules and runs a 1,000-iteration Monte Carlo tournament simulation.

### 1.2. Frontend (Modern Web)
* **Structure & UI**: **HTML5** (semantic structure) & **Vanilla CSS3** (curated design system using custom CSS variables, dark-mode glassmorphism, responsive grid layouts, and smooth animations).
* **Logic & Connectivity**: **Vanilla JavaScript (ES6+)** (manages asynchronous `fetch` requests, role-based authorization headers, custom DOM updates, and sub-tab toggles).
* **Icons**: **Google Material Symbols Outlined** (scalable UI icons).
* **Charts**: **Raw inline SVGs** (rendered dynamically using SVG circle dash-arrays for lightweight, premium charts without third-party JS bundle overhead).

---

## 2. Comprehensive File & Folder Manifest

Below is the purpose and function of every file inside the project directory:

```text
Prasar_Drishti_AI/
├── backend/
│   ├── api/
│   │   ├── auth.py             # Login, logout, current-user, role decorator logic.
│   │   ├── news.py             # Stance trends, manual stance analyzer, and scraper APIs.
│   │   └── sports.py           # World cup simulations, news refresh triggers, Indian news, and medal prospects endpoints.
│   ├── app/
│   │   └── __init__.py         # Flask app factory, blueprints registration, and night scraper cron job.
│   ├── data/
│   │   ├── raw/
│   │   │   ├── archive_articles.json       # Cleaned historical stance dataset.
│   │   │   └── indian_sports_articles.json # Cleaned India-specific sports news dataset.
│   │   └── sports/
│   │       ├── fifa_rankings.csv           # Seeded June 2026 FIFA national rankings.
│   │       ├── world_cup_groups.json       # Seeded 2026 World Cup group stage teams.
│   │       ├── world_cup_group_stage.csv   # Deterministic resolved scores of all group stage games.
│   │       └── world_cup_knockouts_actual.json # Actual completed R32 matches & shootout outcomes.
│   ├── ml/
│   │   ├── train_sentiment.py  # Pipeline training Stance model (TF-IDF + Linear SVM).
│   │   └── train_sports.py     # Pipeline training World Cup prediction model.
│   ├── models/
│   │   ├── stance_model.joblib # Serialized political stance NLP model.
│   │   └── sports_predictor.joblib # Serialized World Cup predictor model.
│   ├── scraper/
│   │   └── newsonair_scraper.py# NewsOnAir scraper core engine.
│   ├── config.py               # Shared path, CORS, and hyperparameter configuration.
│   ├── requirements.txt        # Full backend dependencies manifest.
│   └── run.py                  # Entry point to launch Flask backend at port 5000.
├── frontend/
│   ├── app/
│   │   ├── auth.js             # Form capture, login storage, and JWT token management.
│   │   └── dashboard.js        # Tab switcher, news ticker, SVGs rendering, bracket builder.
│   ├── styles/
│   │   ├── auth.css            # Stylesheets for login panel.
│   │   └── dashboard.css       # Core styling variables, scrollbars, and command layouts.
│   ├── index.html              # Dark glassmorphic login screen.
│   └── dashboard.html          # Main application dashboard shell and split-panels structure.
├── scripts/
│   ├── clean_archive.py        # Utility repairing duplicate paragraphs and sidebar leaks in archive.
│   └── run_news_monitor.py     # Rolling 30-min scraper monitor pipeline.
├── explanation.md              # [This File] Project insights, stack info, and how-to-code guide.
└── README.md                   # Quickstart environment instructions.
```

---

## 3. How to Code This Project From Scratch

If you ever need to recreate this project from scratch, follow these modular steps:

### Step 1: Backend Infrastructure & Configurations
1. **Directory Setup**: Create a workspace folder. Set up standard folders: `backend/api`, `backend/app`, `backend/scraper`, `backend/ml`, `backend/models`, `backend/data`, `frontend/app`, `frontend/styles`, and `scripts`.
2. **Config File (`backend/config.py`)**: Define absolute paths to data directories, model directories, allowed CORS origins (e.g. `http://localhost:3000`), session secrets, and default database filenames.
3. **App Factory (`backend/app/__init__.py`)**: 
   - Define a `create_app()` function that initializes Flask.
   - Attach CORS supports with credentials.
   - Register blueprints (`auth`, `news`, `sports`).
   - Instantiate `BackgroundScheduler` from `apscheduler` and add a job to scrape and archive daily rolling files at 23:55.
4. **Auth Blueprint (`backend/api/auth.py`)**:
   - Write `/login` endpoint matching username/password against a list of mock users (e.g., `admin/admin123` with role `admin`, `user/user123` with role `user`).
   - Return a signed JWT token on success.
   - Write `@role_required("admin")` decorator that checks the authorization header's token claims.

### Step 2: NewsOnAir Scraper Engine & Repair Script
1. **Scraper Class (`backend/scraper/newsonair_scraper.py`)**:
   - Write a `scrape()` method using `requests.get()` to fetch the category list index.
   - Use `BeautifulSoup` to find article links.
   - Implement `_extract_body()` using `div.entry-content` children traversal to extract article text.
   - **Crucial Bug Fixes**: To prevent duplicate paragraphs, only extract immediate child paragraphs (avoiding recursive outer div text). To block sidebar leaks, ignore sidebar nodes (like `most-read-list`).
2. **Archive Cleaner (`scripts/clean_archive.py`)**:
   - Write a repair utility that loads `archive_articles.json`.
   - Iterate over each article, check if the text contains common sidebar elements, slice it off, and run midpoint string checks on consecutive blocks to deduplicate paragraphs. Save the repaired files.

### Step 3: Political Stance NLP Classifier
1. **Data Preprocessing & Vectorization**:
   - In `backend/ml/train_sentiment.py`, load the training CSV (`indian_news_political_stance_dataset.csv`).
   - Use `scikit-learn`'s `TfidfVectorizer(ngram_range=(1,2))` to transform raw text into numeric features.
2. **Custom VADER Feature Injector**:
   - Import `SentimentIntensityAnalyzer` from `nltk.sentiment.vader`.
   - Update VADER's `lexicon` dictionary with customized Indian political weight scores (e.g. `{"inaugurates": 2.0, "protest": -2.0, "strike": -1.5}`).
   - Extract `pos`, `neg`, `neu`, and `compound` scores for each article. Shift compound score (`compound + 1.0` to ensure positive features since Naive Bayes/Linear SVC require non-negative bounds).
3. **Model Selection & Saving**:
   - Combine TF-IDF features with VADER shifted features.
   - Split dataset 80/20. Train `LinearSVC()` and save the trained pipeline (vectorizer + classifier) to `backend/models/stance_model.joblib`.
4. **API Integration (`backend/api/news.py`)**:
   - Write a `/news/sentiment-trends` endpoint that loads government-relevant articles, runs predictions, and counts Pro-Govt (2), Neutral (1), and Anti-Govt (0) stances.

### Step 4: Sports Predictor, Completed Knockout Overrides, & Refreshes
1. **World Cup Groups & Schedules**:
   - Seed team names and rankings into `fifa_rankings.csv`.
   - Define groups inside `world_cup_groups.json` and group stage matches inside `world_cup_group_stage.csv`.
2. **Deterministic & Monte Carlo Tournament Simulation**:
   - In `backend/api/sports.py`, write `simulate_group_deterministic` to calculate standings by assigning 3 points for wins and 1 for draws.
   - Create a file `world_cup_knockouts_actual.json` containing actual scores of completed R32 matches (June 28 – July 1).
   - In `/predictions` and `run_monte_carlo`, load `world_cup_knockouts_actual.json`. Hardcode the official R32 matchups.
   - Override completed matches: set match winner and confidence to 1.0. Restructure `run_monte_carlo` to run simulation paths starting directly from the official 32 participants for accurate leaderboards.
3. **Data Refresh Endpoints**:
   - Write POST `/api/sports/refresh-indian-news` to dynamically load `scrape_indian_sports.py` using `importlib.util` and trigger real-time scraping.
   - Write POST `/api/sports/refresh-world-cup` to merge results of matches 9 and 10 (Belgium vs Senegal, USA vs Bosnia-Herzegovina) into the JSON database.
4. **Medal Prospects API**:
   - Write GET `/api/sports/medal-prospects` route returning top athletes (e.g. Neeraj Chopra, Satwik-Chirag) using valid standard Material Symbols (e.g. `directions_run` and `sports_tennis`).

### Step 5: Frontend Dashboard & Premium Visuals
1. **Design System (`frontend/styles/dashboard.css`)**: Define standard CSS colors using HSL variables (`--primary`, `--secondary`, `--background`, `--surface-container-high`).
2. **Dashboard Layout (`frontend/dashboard.html`)**:
   - Build a sidebar with tab triggers.
   - Split the Sports tab into sub-navigation buttons: **FIFA World Cup** and **Indian Sports**.
   - Create a side-by-side grid inside the **Indian Sports** panel: News feed on the left, and **India's Medal Prospects** card list on the right.
3. **Frontend Controller (`frontend/app/dashboard.js`)**:
   - Fetch stance trends and render SVG circles using `stroke-dasharray` to display donut charts.
   - Fetch predictions and draw the bracket tree. Use the `outcome` field if present (e.g. `"Morocco Win (Actual: 1-1, 3-2 pens)"`).
   - Fetch prospects and render cards showing discipline details and Google icons.

---

## 4. Current Data Statistics & Stance Distributions

Following scraper repairs, archive cleanup, and sports overrides, our stance distributions and news databases are fully calibrated:

### 4.1. Stance Distribution
* **Pro-Government (Stance 2)**: Heavily represented in scraped articles (due to state media bias).
* **Neutral (Stance 1)**: Second most common (mostly factual developmental updates).
* **Anti-Government (Stance 0)**: Small but present (mostly protests, strikes, or inflation updates).

### 4.2. Sports Data Distribution
* **Indian Sports News (Filtered)**: **175 unique articles** (real-time crawler successfully added 3 new compliant articles).
* **FIFA World Cup predictions**:
  - The first 8 completed R32 matches are locked in initially (June 28 – July 1) with 100% confidence.
  - Matches 9 and 10 (July 2) are completed with actual scores upon refresh.
  - Matches 11 to 16 (July 3) remain as upcoming predicted slots.
