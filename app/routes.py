from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models import Project
from app.scraper import fetch_projects

main = Blueprint("main", __name__)

@main.route("/")
def dashboard():
    """Render the dashboard page with projects."""
    projects = Project.query.all()
    return render_template('dashboard.html', projects=projects)

@main.route("/projects")
def get_projects():
    """Fetch all projects as JSON."""
    projects = Project.query.all()
    return jsonify([{"title": p.title, "description": p.description, "url": p.url} for p in projects])

@main.route("/scrape", methods=["GET", "POST"])
def scrape():
    """Manually trigger the scraper."""
    fetch_projects()
    return jsonify({"message": "Scraper executed successfully!"})
