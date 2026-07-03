from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from api.auth import auth_bp
from api.news import news_bp
from api.sports import sports_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    CORS(
        app,
        origins=Config.FRONTEND_ORIGINS,
        supports_credentials=True,
    )

    Config.create_dirs()
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(news_bp, url_prefix="/api/news")
    app.register_blueprint(sports_bp, url_prefix="/api/sports")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "prasar-drishti-ai"})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "API route not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"message": "Server error", "error": str(error)}), 500

    # Start daily background news scraper at night (23:55)
    app.scheduler = None
    import os
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import date
        
        def scheduled_scrape_and_archive():
            app.logger.info("Executing scheduled daily scrape and archive...")
            try:
                from scraper.newsonair_scraper import NewsOnAirScraper
                scraper = NewsOnAirScraper(delay=0.3)
                today = date.today()
                
                # Scrape today's data (limit per category: 40, max pages: 3)
                articles = scraper.scrape(
                    categories=["national", "international", "business", "sports", "miscellaneous"],
                    limit_per_category=40,
                    max_pages=3,
                    start_date=today,
                    end_date=today,
                    government_only=False,
                )
                
                # Save to today's file
                today_stem = f"today_{today.isoformat()}"
                scraper.save(articles, stem=today_stem, merge_existing=True)
                
                # Save directly into archive_articles (scraped to archive of everyday)
                paths = scraper.save(articles, stem="archive_articles", merge_existing=True)
                app.logger.info(f"Scheduled scrape complete: {len(articles)} articles archived. Paths: {paths}")
                
            except Exception as e:
                app.logger.error(f"Scheduled scrape and archive failed: {e}", exc_info=True)

        scheduler = BackgroundScheduler()
        # Schedule the job to run every day at night (23:55 local time of the user's OS)
        scheduler.add_job(scheduled_scrape_and_archive, 'cron', hour=23, minute=55, id='daily_news_scrape')
        scheduler.start()
        app.scheduler = scheduler
        app.logger.info("Daily news scraper scheduled for 23:55 local time every night.")

    return app
