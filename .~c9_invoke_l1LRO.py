import os
import requests
import urllib.parse
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from datetime import datetime

import pembantu

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def home():
    return render_template("cari.html")

@app.route("/kiblat")
def kiblat():
    return render_template("kiblat.html")

@app.route("/jadwal", methods=["GET", "POST"])
def jadwal():
    if request.method == "POST":
        address = request.form.get("kota")
        method = request.form.get("method")
        month = request.form.get("month")
        year = request.form.get("year")
        try:
            loc = address.lower()
            response = requests.get(f"https://api.aladhan.com/v1/calendarByAddress?address={urllib.parse.quote_plus(loc)}&method={urllib.parse.quote_plus(method)}&month={urllib.parse.quote_plus(month)}&year={urllib.parse.quote_plus(year)}")
            response.raise_for_status()
        except requests.RequestException:
            return None
        # Parse response
        try:
            jd = response.json()["data"]
            n = len(jd)
            monthName = jd[0].date.gregorian.month.en
            yearName = jd[0].date.gregorian.year
            return render_template("jadwal.html", jd = jd, n = n, address=address, monthName=monthName, )
        except (KeyError, TypeError, ValueError):
            return render_template("apology.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("apology.html")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
