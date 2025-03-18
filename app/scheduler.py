from apscheduler.schedulers.background import BackgroundScheduler
from app.scraper import fetch_projects

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_projects, "interval", hours=1)
scheduler.start()
