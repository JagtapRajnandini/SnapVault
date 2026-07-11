from flask import render_template
from SnapVault import app


"""@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")"""


@app.route("/dashboard")
def dashboard_page():
    return "<h2>Dashboard - Coming Soon</h2>"