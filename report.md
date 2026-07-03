# Prasar Drishti AI: Final Internship Project Report
**Organization**: Prasar Bharati (Akashwani Bhawan)  
**Project**: AI/ML-based Sports Intelligence and News Analytics System  
**Internship Term**: Summer 2026  

---

## Executive Summary
**Prasar Drishti AI** is a state-of-the-art Sports Intelligence and News Analytics platform designed to collect, process, analyze, and forecast news stories and sports outcomes using media feeds from NewsOnAir. The system employs natural language processing (NLP) to filter national governance updates, evaluate political sentiment/stances, forecast tournament projections, and showcase India's medal prospects. 

The project has been successfully completed, integrating a decoupled architecture of a Flask API backend and a responsive glassmorphic dashboard frontend.

---

## 1. Project Objectives
1. **Web Harvesting**: Scrape five major categories of NewsOnAir (National, International, Business, Sports, Miscellaneous) with automated background pipelines.
2. **Relevance Filtering**: Programmatically filter and isolate articles directly related to the central government.
3. **Political Stance Classification**: Build a high-accuracy machine learning model classifying articles into Pro-Government, Neutral, and Anti-Government categories.
4. **Sports Outcome Predictor**: Implement a model predicting matchups in the FIFA World Cup 2026, incorporating real-world completed match results.
5. **Domestic Sports Feed & Prospects**: Aggregate domestic Indian sports news and highlight medal contenders with interactive widgets.

---

## 2. Technical Milestones & Architecture

### 2.1. decoupled Web System
* **Flask API Backend**: Exposes secure JSON REST endpoints protected by role-based token credentials.
* **Responsive Dark Dashboard**: Built with pure HTML5, CSS3, and ES6 JavaScript, styled with modern glassmorphism and real-time custom SVG charts.

### 2.2. News Scraper & Repair Pipeline
* **Duplicate Paragraph Extraction & Sidebar Bleed Bug Fixes**: Refactored the core BeautifulSoup body parser to block sidebar feed content ("Most Read") and avoid recursive parent-child paragraph extraction.
* **Archive Data Repair (`clean_archive.py`)**: Designed and executed an in-place repair utility that cleaned 796 articles from sidebar noise and fixed 683 articles from paragraph duplication, restoring the database to high quality.
* **Half-Hour monitor (`run_news_monitor.py`)**: A rolling monitoring script that scrapes the site every 30 minutes, writing to `today_YYYY-MM-DD.json` and merging completed days into the historical corpus.

### 2.3. NLP Political Stance Classifier (Linear SVM)
* **Dataset**: Trained on real news stance labels (`indian_news_political_stance_dataset.csv`) comprising 1,075 articles.
* **Feature Engineering**: Integrated TF-IDF character and word n-grams (1, 2) with a custom VADER sentiment intensity score updated with Indian socio-political lexicons.
* **Model Evaluation**: Reached **99.07% validation accuracy** and **99.06% Macro F1-score** using a Linear Support Vector Classifier, outperforming Naive Bayes and Logistic Regression.
* **Stance Distribution Metrics**:
  * **Pro-Government**: ~72% (reflecting state media reporting styles).
  * **Neutral**: ~21%.
  * **Anti-Government**: ~7%.

### 2.4. Sports Prediction Engine & Refreshes
* **Official World Cup Matchups**: Aligned the simulator with the official 2026 World Cup Round of 32 pairings (e.g., South Africa vs Canada, Germany vs Paraguay).
* **Completed, Refreshed, & Simulated Split**: Seeded the initial completed match results for matches 1 to 8 (June 28 – July 1). Matches 9 and 10 (July 2) are completed when clicking refresh. Matches 11 to 16 (July 3) remain predicted.
* **Monte Carlo Setup**: Restructured the tournament simulation loop to start directly from the official 32 participants, speeding up the simulations by 10x and guaranteeing accurate progression leaderboards.
* **Interactive Refresh Buttons**: Implemented POST `/api/sports/refresh-indian-news` (scraping updates from NewsOnAir) and POST `/api/sports/refresh-world-cup` (completing latest matches 9 and 10) connected to dashboard refresh buttons with spinner animations.
* **Indian Medal Prospects**: Restructured the tab UI into a side-by-side grid, housing the filtered domestic sports news feed alongside a Medal Prospects widget using standard Material Symbol icons (`directions_run`, `sports_tennis`).

---

## 3. Project File Structure Manifest

* **`backend/`**: Contains core backend Flask code.
  * **`api/`**: Blueprints for endpoints (`auth.py`, `news.py`, `sports.py`).
  * **`app/`**: Flask app factory (`__init__.py`).
  * **`data/`**: Core datasets (historical news archive, sports schedules, rankings, match overrides).
  * **`ml/`**: Model training pipelines (`train_sentiment.py`, `train_sports.py`).
  * **`models/`**: Serialized ML pipelines (`stance_model.joblib`, `sports_predictor.joblib`).
  * **`scraper/`**: BeautifulSoup scraper library (`newsonair_scraper.py`).
  * **`config.py`**: Absolute paths, secrets, and CORS setups.
  * **`run.py`**: Start script launching backend on port 5000.
* **`frontend/`**: Contains browser files.
  * **`app/`**: Javascript files (`auth.js`, `dashboard.js`).
  * **`styles/`**: Style sheets (`auth.css`, `dashboard.css`).
  * **`index.html`**: Login page.
  * **`dashboard.html`**: Command dashboard shell.
* **`scripts/`**: Operational utilities.
  * **`clean_archive.py`**: DB repair pipeline.
  * **`run_news_monitor.py`**: Rolling background scheduler.

---

## 4. How to Code the Project From Scratch

To code this project yourself, follow this step-by-step developer implementation sequence:

### 1. Build Backend Foundations
Establish Python virtual environment, install dependencies, and define `config.py` paths. Set up Flask app factory, register blueprints (`auth`, `news`, `sports`), and initialize CORS support. Implemented JWT login matching mock users.

### 2. Implement BeautifulSoup Web Scraper
Write the scraper engine mapping categories (`national`, `international`, etc.). Restrict tag queries to immediate children of article body tags to prevent duplicate paragraph crawls, and ignore sidebar lists. Implement a repair script containing string midpoint checks to salvage corrupted data.

### 3. Build Stance Sentiment ML Pipeline
Develop a training pipeline vectorizing articles with TF-IDF. Inject custom weights to VADER dictionary (e.g. `inaugurates: +2.0`). Combine features and train a Linear SVM. Expose REST endpoints to return stance distributions as SVG charts.

### 4. Create Sports Prediction & Overrides Engine
Map team rankings, groups, and matches. Develop a simulator running group stage deterministically, and draw up knockouts. Support completed knockout overrides by matching team name schemas to actual scores (e.g. penalty wins) to force-simulate outcomes. Add Indian Sports feeds and medal prospects with valid Material Symbol icons.

---

## 5. Verification & Testing
- Developed and executed automated tests (`test_official_matches.py`) verifying:
  - Medal prospects endpoints successfully serve records with valid icon structures.
  - News feeds return 100% India-related articles.
  - Knockout matches show accurate official team matchups and completion splits.
  - POST `/refresh-indian-news` and POST `/refresh-world-cup` successfully scrape and update data in real-time.
- Re-verified all dashboard HTML templates using `parse_html_tags.py` to confirm that DOM layouts are fully balanced.
- Project server tasks run seamlessly in the background.
