import json
from pathlib import Path
from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from api.auth import login_required, role_required
from config import Config

news_bp = Blueprint("news", __name__)

CATEGORIES = {"sports", "national", "international", "business"}
CATEGORIES_WITH_MISC = {"sports", "national", "international", "business", "miscellaneous"}


def articles_path(dataset: str = "default") -> Path:
    stems = {
        "default": "newsonair_articles",
        "archive": "archive_articles",
        "today": f"today_{date.today().isoformat()}",
        "thehindu": "thehindu_articles",
        "thehindu_archive": "thehindu_articles",
        "thehindu_today": f"today_thehindu_{date.today().isoformat()}",
    }
    stem = stems.get(dataset, "newsonair_articles")
    return Path(Config.RAW_DIR) / f"{stem}.json"


@news_bp.get("/articles")
@login_required
def articles():
    dataset = request.args.get("dataset", "default")
    path = articles_path(dataset)
    if not path.exists():
        return jsonify({"articles": [], "message": "No scraped data found yet."})

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return jsonify({"articles": [], "message": "Saved scraped data is not valid JSON."}), 500

    category = request.args.get("category")
    limit = request.args.get("limit", "50")

    if not limit.isdigit():
        return jsonify({"message": "limit must be a number"}), 400

    limit = min(int(limit), 100)

    if category:
        data = [article for article in data if article.get("category") == category]

    return jsonify({"articles": data[:limit], "count": len(data[:limit]), "dataset": dataset})


@news_bp.post("/scrape")
@role_required("admin")
def scrape():
    payload = request.get_json(silent=True) or {}
    categories = payload.get("categories") or ["national", "international", "business", "sports", "miscellaneous"]
    limit = int(payload.get("limit", 5))
    days = int(payload.get("days", 1))
    pages = int(payload.get("pages", 3))
    government_only = bool(payload.get("government_only", False))
    dataset = payload.get("dataset", "today")

    invalid_categories = [category for category in categories if category not in CATEGORIES_WITH_MISC]
    if invalid_categories:
        return jsonify({"message": f"Invalid categories: {', '.join(invalid_categories)}"}), 400

    try:
        from scraper.newsonair_scraper import NewsOnAirScraper

        scraper = NewsOnAirScraper(delay=0.3)
        end_date = date.today()
        start_date = end_date - timedelta(days=max(days - 1, 0))
        stem = f"today_{end_date.isoformat()}" if dataset == "today" else "archive_articles"
        scraped_articles = scraper.scrape(
            categories,
            limit_per_category=min(limit, 50),
            max_pages=min(pages, 20),
            start_date=start_date,
            end_date=end_date,
            government_only=government_only,
        )
        paths = scraper.save(scraped_articles, stem=stem, merge_existing=True)
    except ModuleNotFoundError as exc:
        return (
            jsonify(
                {
                    "message": "Scraper dependency missing",
                    "error": f"{exc}. Run: python -m pip install -r requirements-scraper.txt",
                }
            ),
            500,
        )
    except Exception as exc:
        return jsonify({"message": "Scrape failed", "error": str(exc)}), 500

    return jsonify(
        {
            "message": "Scrape complete",
            "count": len(scraped_articles),
            "dataset": dataset,
            "files": paths,
        }
    )


@news_bp.post("/scrape-last-month")
@role_required("admin")
def scrape_last_month():
    import threading

    def run_background_scrape():
        try:
            from scraper.newsonair_scraper import NewsOnAirScraper

            scraper = NewsOnAirScraper(delay=0.3)
            today = date.today()
            articles = scraper.scrape(
                categories=["national", "international", "business", "sports", "miscellaneous"],
                limit_per_category=300,
                max_pages=35,
                start_date=today - timedelta(days=30),
                end_date=today,
                government_only=False,
            )
            scraper.save(articles, stem="archive_articles", merge_existing=True)
            print("Background last-month scrape completed successfully.")
        except Exception as exc:
            print(f"Background last-month scrape failed: {exc}")

    try:
        threading.Thread(target=run_background_scrape, daemon=True).start()
    except Exception as exc:
        return jsonify({"message": "Failed to start background scrape thread", "error": str(exc)}), 500

    return jsonify({
        "message": "Historical scrape started in the background. It will populate the archive over the next few minutes."
    })


@news_bp.post("/scrape-thehindu-last-month")
@role_required("admin")
def scrape_thehindu_last_month():
    import threading

    def run_background_scrape():
        try:
            from scraper.thehindu_scraper import TheHinduScraper

            scraper = TheHinduScraper(delay=0.5)
            today = date.today()
            articles = scraper.scrape(
                categories=["national", "international", "business", "sports", "miscellaneous"],
                limit_per_category=300,
                max_pages=20,
                start_date=today - timedelta(days=30),
                end_date=today,
                government_only=False,
            )
            scraper.save(articles, stem="thehindu_articles", merge_existing=True)
            print("Background The Hindu last-month scrape completed successfully.")
        except Exception as exc:
            print(f"Background The Hindu last-month scrape failed: {exc}")

    try:
        threading.Thread(target=run_background_scrape, daemon=True).start()
    except Exception as exc:
        return jsonify({"message": "Failed to start background scrape thread", "error": str(exc)}), 500

    return jsonify({
        "message": "Historical The Hindu scrape started in the background. It will populate the archive over the next few minutes."
    })


@news_bp.post("/archive-today")
@role_required("admin")
def archive_today_route():
    try:
        from scraper.newsonair_scraper import archive_today

        paths = archive_today()
    except Exception as exc:
        return jsonify({"message": "Archive failed", "error": str(exc)}), 500

    if not paths:
        return jsonify({"message": "No today's data found to archive", "count": 0})
    return jsonify({"message": "Today's data merged into archive", "files": paths})


@news_bp.post("/train-sentiment")
@role_required("admin")
def train_sentiment_route():
    try:
        from ml.train_sentiment import train_and_evaluate_models
        metadata = train_and_evaluate_models()
        return jsonify({
            "message": "Sentiment model trained successfully",
            "metadata": metadata
        })
    except Exception as exc:
        return jsonify({"message": "Failed to train model", "error": str(exc)}), 500


@news_bp.get("/sentiment-model-info")
@login_required
def sentiment_model_info():
    metadata_path = Path(Config.SENTIMENT_MODEL_DIR) / "model_metadata.json"
    if not metadata_path.exists():
        return jsonify({
            "trained": False,
            "message": "Model is not trained yet. Heuristic sentiment analysis is active."
        })
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["trained"] = True
        return jsonify(metadata)
    except Exception as exc:
        return jsonify({"message": "Failed to load model metadata", "error": str(exc)}), 500


@news_bp.post("/analyze-sentiment")
@login_required
def analyze_sentiment():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not text:
        return jsonify({"message": "Missing 'text' in request body"}), 400
        
    try:
        from ml.train_sentiment import load_model_and_predict
        label_id, confidence, method = load_model_and_predict(text)
        label_map = {0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt"}
        return jsonify({
            "text": text,
            "sentiment_label": label_id,
            "sentiment_name": label_map.get(label_id, "Neutral"),
            "sentiment_confidence": confidence,
            "classification_method": method
        })
    except Exception as exc:
        return jsonify({"message": "Failed to analyze sentiment", "error": str(exc)}), 500


def is_indian_govt_article(article: dict) -> bool:
    category = article.get("category", "")
    title_body = f"{article.get('title', '')} {article.get('summary', '')} {article.get('body', '')}".lower()
    
    # Exclude sports category entirely, unless it specifically mentions funding/ministry/policy
    if category == "sports":
        sports_govt_kws = ["ministry of youth affairs", "sports ministry", "sports minister", "khelo india", "tops scheme", "funding", "allocation"]
        if not any(kw in title_body for kw in sports_govt_kws):
            return False
            
    # Keywords indicating Indian government leaders, ministries, and central bodies
    indian_govt_kws = [
        "modi", "pm ", "prime minister", "president murmu", "droupadi murmu", 
        "amit shah", "rajnapth", "jaishankar", "finance minister", "sitharaman", 
        "mansukh mandaviya", "union minister", "cabinet minister", "central government", 
        "union government", "parliament", "lok sabha", "rajya sabha", "supreme court", 
        "election commission", "cabinet", "ministry of", "yojana", "khelo india", 
        "fssai", "nta", "neet", "national testing agency", "prasar bharati", "akashwani"
    ]
    
    # Must mention at least one of these Indian government indicators
    if not any(kw in title_body for kw in indian_govt_kws):
        return False
        
    # Exclude articles about foreign governments
    if category == "international":
        # Must explicitly contain India/Indian keywords to be relevant (e.g. bilateral affairs)
        india_refs = ["india", "indian", "modi", "delhi", "jaishankar", "bharat", "new delhi"]
        if not any(kw in title_body for kw in india_refs):
            return False
            
    # Filter out purely foreign government matches (if they don't also mention India)
    foreign_exclusions = [
        "us president", "joe biden", "donald trump", "white house",
        "pakistan prime minister", "imran khan", "shehbaz sharif",
        "uk prime minister", "rishi sunak", "keir starmer", "downing street"
    ]
    if any(fb in title_body for fb in foreign_exclusions):
        if not any(kw in title_body for kw in ["india", "indian", "modi", "delhi", "jaishankar", "bilateral"]):
            return False
            
    return True


def get_sentiment_trends_data(dataset: str, admin_view: bool = False) -> dict | None:
    path = articles_path(dataset)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not data:
        return {
            "articles": [],
            "distribution": {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0},
            "category_breakdown": {},
            "timeline": {},
            "count": 0,
            "dataset": dataset
        }

    # Filter data to only consider Indian Government related articles
    filtered_data = [art for art in data if is_indian_govt_article(art)]
    
    # Filter by visibility if not admin_view
    if not admin_view:
        filtered_data = [art for art in filtered_data if art.get("is_visible", True)]
    
    if not filtered_data:
        return {
            "articles": [],
            "distribution": {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0},
            "category_breakdown": {},
            "timeline": {},
            "count": 0,
            "dataset": dataset
        }

    # Prepare texts for batch prediction
    texts = []
    for article in filtered_data:
        title = article.get("title", "")
        summary = article.get("summary", "")
        body = article.get("body", "")
        texts.append(f"{title} {summary} {body}")

    try:
        from ml.train_sentiment import load_model_and_predict_batch
        predictions = load_model_and_predict_batch(texts)
    except Exception as exc:
        # Fallback inline classifier
        predictions = []
        for text in texts:
            predictions.append((1, 0.70, "fallback"))

    # Augment articles and compute aggregates
    # Labels map: 0 -> Anti-Govt, 1 -> Neutral, 2 -> Pro-Govt
    label_map = {0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt"}
    
    distribution = {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0}
    category_breakdown = {}
    timeline = {}

    augmented_articles = []
    for idx, (article, pred) in enumerate(zip(filtered_data, predictions)):
        manual_label = article.get("manual_sentiment_label")
        if manual_label is not None:
            label_id = int(manual_label)
            confidence = 1.0
            method = "manual_override"
        else:
            label_id, confidence, method = pred
            
        label_name = label_map.get(label_id, "Neutral")
        
        art_copy = dict(article)
        art_copy["sentiment_label"] = label_id
        art_copy["sentiment_name"] = label_name
        art_copy["sentiment_confidence"] = confidence
        art_copy["classification_method"] = method
        
        # Keep track of custom tags
        art_copy["is_visible"] = article.get("is_visible", True)
        art_copy["manual_sentiment_label"] = manual_label
        
        augmented_articles.append(art_copy)
        
        # Overall distribution
        distribution[label_name] += 1
        
        # Category breakdown
        cat = article.get("category", "miscellaneous")
        if cat not in category_breakdown:
            category_breakdown[cat] = {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0, "total": 0}
        category_breakdown[cat][label_name] += 1
        category_breakdown[cat]["total"] += 1
        
        # Timeline (by published_date or date part of published_at)
        pub_date = article.get("published_date")
        if not pub_date:
            pub_at = article.get("published_at", "")
            if pub_at:
                try:
                    from datetime import datetime
                    pub_date = datetime.strptime(pub_at, "%B %d, %Y %I:%M %p").date().isoformat()
                except Exception:
                    pub_date = "Unknown"
            else:
                pub_date = "Unknown"
                
        if pub_date not in timeline:
            timeline[pub_date] = {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0, "total": 0}
        timeline[pub_date][label_name] += 1
        timeline[pub_date]["total"] += 1

    return {
        "articles": augmented_articles,
        "distribution": distribution,
        "category_breakdown": category_breakdown,
        "timeline": timeline,
        "count": len(augmented_articles),
        "dataset": dataset
    }


@news_bp.get("/sentiment-trends")
@login_required
def sentiment_trends():
    dataset = request.args.get("dataset", "default")
    admin_view = request.args.get("admin_view", "false").lower() == "true"
    
    data = get_sentiment_trends_data(dataset, admin_view)
    if data is None:
        return jsonify({
            "articles": [],
            "distribution": {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0},
            "category_breakdown": {},
            "timeline": {},
            "message": "No scraped data found yet."
        })
        
    return jsonify(data)


def add_feedback_label(text_feature, label_id):
    import csv
    path = Path(Config.LABELLED_DIR) / "feedback_labels.csv"
    existing = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing[row["text_feature"]] = int(row["label_id"])
        except Exception:
            pass
            
    existing[text_feature] = int(label_id)
    
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text_feature", "label_id"])
            writer.writeheader()
            for text, lbl in existing.items():
                writer.writerow({"text_feature": text, "label_id": lbl})
    except Exception as e:
        print(f"Error saving feedback label: {e}")


@news_bp.post("/toggle-visibility")
@role_required("admin")
def toggle_visibility():
    payload = request.get_json(silent=True) or {}
    url = payload.get("url")
    dataset = payload.get("dataset", "today")
    is_visible = bool(payload.get("is_visible", True))
    
    if not url:
        return jsonify({"message": "Missing 'url' in request body"}), 400
        
    path = articles_path(dataset)
    if not path.exists():
        return jsonify({"message": "Dataset file not found"}), 404
        
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        updated = False
        for art in data:
            if art.get("url") == url:
                art["is_visible"] = is_visible
                updated = True
                break
                
        if updated:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            # Update the CSV copy as well
            csv_path = path.with_suffix(".csv")
            if csv_path.exists():
                import csv
                fieldnames = [
                    "title", "url", "category", "published_at", "published_date",
                    "summary", "body", "word_count", "is_government_related", "scraped_at",
                    "is_visible", "manual_sentiment_label", "manual_sentiment_name"
                ]
                with open(csv_path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(data)
            return jsonify({"message": f"Article visibility set to {is_visible}"})
        else:
            return jsonify({"message": "Article not found in dataset"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to toggle visibility", "error": str(e)}), 500


@news_bp.post("/override-sentiment")
@role_required("admin")
def override_sentiment():
    payload = request.get_json(silent=True) or {}
    url = payload.get("url")
    dataset = payload.get("dataset", "today")
    label = payload.get("label") # 0, 1, or 2, or None to clear override
    
    if not url:
        return jsonify({"message": "Missing 'url' in request body"}), 400
        
    path = articles_path(dataset)
    if not path.exists():
        return jsonify({"message": "Dataset file not found"}), 404
        
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        updated = False
        target_article = None
        for art in data:
            if art.get("url") == url:
                if label is None:
                    art.pop("manual_sentiment_label", None)
                    art.pop("manual_sentiment_name", None)
                else:
                    label_id = int(label)
                    label_map = {0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt"}
                    art["manual_sentiment_label"] = label_id
                    art["manual_sentiment_name"] = label_map.get(label_id, "Neutral")
                target_article = art
                updated = True
                break
                
        if updated:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            
            # Update CSV copy
            csv_path = path.with_suffix(".csv")
            if csv_path.exists():
                import csv
                fieldnames = [
                    "title", "url", "category", "published_at", "published_date",
                    "summary", "body", "word_count", "is_government_related", "scraped_at",
                    "is_visible", "manual_sentiment_label", "manual_sentiment_name"
                ]
                with open(csv_path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(data)

            # Append to feedback loop for model learning
            if label is not None and target_article:
                text_feature = f"{target_article.get('title', '')} {target_article.get('body', '')}"
                add_feedback_label(text_feature, label)
                
            return jsonify({"message": "Sentiment override saved successfully"})
        else:
            return jsonify({"message": "Article not found in dataset"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to override sentiment", "error": str(e)}), 500


@news_bp.get("/keyword-rules")
@login_required
def get_keyword_rules():
    rules_path = Path(Config.LABELLED_DIR) / "keyword_rules.json"
    if not rules_path.exists():
        return jsonify({})
    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        return jsonify(rules)
    except Exception as e:
        return jsonify({"message": "Failed to load keyword rules", "error": str(e)}), 500


@news_bp.post("/save-keyword-rule")
@role_required("admin")
def save_keyword_rule():
    payload = request.get_json(silent=True) or {}
    keyword = payload.get("keyword", "").strip()
    label = payload.get("label")
    
    if not keyword or label is None:
        return jsonify({"message": "Missing 'keyword' or 'label'"}), 400
        
    rules_path = Path(Config.LABELLED_DIR) / "keyword_rules.json"
    rules = {}
    if rules_path.exists():
        try:
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    rules[keyword] = int(label)
    
    try:
        rules_path.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
        return jsonify({"message": f"Keyword rule saved: '{keyword}' -> label {label}"})
    except Exception as e:
        return jsonify({"message": "Failed to save keyword rule", "error": str(e)}), 500


@news_bp.post("/delete-keyword-rule")
@role_required("admin")
def delete_keyword_rule():
    payload = request.get_json(silent=True) or {}
    keyword = payload.get("keyword", "").strip()
    
    if not keyword:
        return jsonify({"message": "Missing 'keyword'"}), 400
        
    rules_path = Path(Config.LABELLED_DIR) / "keyword_rules.json"
    if not rules_path.exists():
        return jsonify({"message": "No rules found"}), 404
        
    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        if keyword in rules:
            del rules[keyword]
            rules_path.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
            return jsonify({"message": f"Deleted rule for keyword '{keyword}'"})
        return jsonify({"message": "Keyword rule not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete keyword rule", "error": str(e)}), 500


@news_bp.get("/scheduler-jobs")
@role_required("admin")
def get_scheduler_jobs():
    from flask import current_app
    scheduler = getattr(current_app, "scheduler", None)
    if not scheduler:
        return jsonify({"message": "Scheduler is not active", "jobs": []}), 200
        
    jobs = []
    try:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
    except Exception as e:
        return jsonify({"message": "Failed to get jobs", "error": str(e)}), 500
        
    return jsonify({"jobs": jobs})


@news_bp.post("/scrape-thehindu")
@role_required("admin")
def scrape_thehindu():
    payload = request.get_json(silent=True) or {}
    categories = payload.get("categories") or ["national", "international", "business", "sports", "miscellaneous"]
    limit = int(payload.get("limit", 5))
    days = int(payload.get("days", 1))
    pages = int(payload.get("pages", 3))
    government_only = bool(payload.get("government_only", False))
    dataset = payload.get("dataset", "thehindu_today")

    invalid_categories = [category for category in categories if category not in CATEGORIES_WITH_MISC]
    if invalid_categories:
        return jsonify({"message": f"Invalid categories: {', '.join(invalid_categories)}"}), 400

    try:
        from scraper.thehindu_scraper import TheHinduScraper

        scraper = TheHinduScraper(delay=0.5)
        end_date = date.today()
        start_date = end_date - timedelta(days=max(days - 1, 0))
        stem = f"today_thehindu_{end_date.isoformat()}" if dataset == "thehindu_today" else "thehindu_articles"
        scraped_articles = scraper.scrape(
            categories,
            limit_per_category=min(limit, 50),
            max_pages=min(pages, 20),
            start_date=start_date,
            end_date=end_date,
            government_only=government_only,
        )
        paths = scraper.save(scraped_articles, stem=stem, merge_existing=True)
    except ModuleNotFoundError as exc:
        return (
            jsonify(
                {
                    "message": "Scraper dependency missing",
                    "error": f"{exc}.",
                }
            ),
            500,
        )
    except Exception as exc:
        return jsonify({"message": "The Hindu scrape failed", "error": str(exc)}), 500

    return jsonify(
        {
            "message": "The Hindu scrape complete",
            "count": len(scraped_articles),
            "dataset": dataset,
            "files": paths,
        }
    )


@news_bp.get("/sentiment-comparison")
@login_required
def sentiment_comparison():
    admin_view = request.args.get("admin_view", "false").lower() == "true"
    noa_dataset = request.args.get("noa_dataset", "archive")
    hindu_dataset = request.args.get("hindu_dataset", "thehindu_archive")

    noa_data = get_sentiment_trends_data(noa_dataset, admin_view) or {
        "distribution": {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0},
        "category_breakdown": {},
        "timeline": {},
        "count": 0
    }
    
    hindu_data = get_sentiment_trends_data(hindu_dataset, admin_view) or {
        "distribution": {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0},
        "category_breakdown": {},
        "timeline": {},
        "count": 0
    }

    return jsonify({
        "newsonair": {
            "distribution": noa_data.get("distribution"),
            "category_breakdown": noa_data.get("category_breakdown"),
            "timeline": noa_data.get("timeline"),
            "count": noa_data.get("count"),
        },
        "thehindu": {
            "distribution": hindu_data.get("distribution"),
            "category_breakdown": hindu_data.get("category_breakdown"),
            "timeline": hindu_data.get("timeline"),
            "count": hindu_data.get("count"),
        }
    })
