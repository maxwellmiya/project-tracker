import requests
import time
import random
import json
from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Flask App Setup
app = Flask(__name__)

# PostgreSQL Database Config (Change for Your DB)
DATABASE_URL = "postgresql://username:password@localhost:5432/projects_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define Project Model
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)

# Create Database Tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Selenium Configuration
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Headers for Requests
HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"},
]

# Target Websites
TARGET_SITES = [
    {"name": "UNGM", "url": "https://www.ungm.org/Public/Notice", "dynamic": False, "selectors": {"project": "div.notice-title", "title": "h2", "desc": "p", "link": "a"}},
    {"name": "ReliefWeb", "url": "https://reliefweb.int/updates?advanced-search=%28S13115%29", "dynamic": False, "selectors": {"project": "div.rw-card", "title": "h3", "desc": "p", "link": "a"}},
    {"name": "DevelopmentAid", "url": "https://www.developmentaid.org/tenders", "dynamic": True, "selectors": {"project": "div.tender", "title": "h2", "desc": "p", "link": "a"}},
    {"name": "IFC", "url": "https://www.ifc.org/en/about/procurement", "dynamic": False, "selectors": {"project": "li.procurement-item", "title": "h3", "desc": "p", "link": "a"}},
]

def fetch_projects(site):
    """Scrape projects from a target website."""
    print(f"Scraping {site['name']}...")

    if site["dynamic"]:
        driver.get(site["url"])
        time.sleep(5)  # Wait for JavaScript to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
    else:
        headers = random.choice(HEADERS)
        response = requests.get(site["url"], headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {site['name']}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")

    projects_data = []
    projects = soup.find_all("div", class_=site["selectors"]["project"])

    for project in projects:
        try:
            title = project.find(site["selectors"]["title"]).text.strip()
            description = project.find(site["selectors"]["desc"]).text.strip()
            project_url = project.find(site["selectors"]["link"])["href"]

            # Avoid Duplicates
            if not session.query(Project).filter_by(title=title).first():
                new_project = Project(title=title, description=description, url=project_url)
                session.add(new_project)
                session.commit()
                projects_data.append({"title": title, "description": description, "url": project_url})
        except Exception as e:
            print(f"Error parsing project: {e}")

    return projects_data

@app.route("/scrape", methods=["GET"])
def scrape_all():
    """Trigger scraper via API."""
    all_projects = []
    for site in TARGET_SITES:
        all_projects.extend(fetch_projects(site))

    return jsonify({"status": "success", "projects": all_projects})

@app.route("/")
def dashboard():
    """Render project dashboard."""
    projects = session.query(Project).all()
    return render_template("dashboard.html", projects=projects)

if __name__ == "__main__":
    app.run(debug=True)
