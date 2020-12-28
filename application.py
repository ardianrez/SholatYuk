import os
import requests
import urllib.parse
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from datetime import datetime, date

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

@app.route("/gettoday")
def today():
    return render_template("gettoday.html")

@app.route("/timetable", methods=["GET", "POST"])
def jadwal():
    if request.method == "POST":
        address = request.form.get("kota")
        method = request.form.get("method")
        month = request.form.get("month")
        year = request.form.get("year")
        now = datetime.now()
        datetoday = now.strftime("%d")
        yeartoday = now.strftime("%Y")
        monthtoday = now.strftime("%02m")
        if month == monthtoday and year == yeartoday:
            date = int(datetoday)
        else:
            date = None
        try:
            response = requests.get(f"https://api.aladhan.com/v1/calendarByAddress?address={urllib.parse.quote_plus(address)}&method={urllib.parse.quote_plus(method)}&month={urllib.parse.quote_plus(month)}&year={urllib.parse.quote_plus(year)}")
            response.raise_for_status()
        except requests.RequestException:
            return None
        # Parse response
        try:
            jd = response.json()["data"]
            n = len(jd)
            return render_template("timetable.html", jd = jd, n = n, address=address, date=date)
        except (KeyError, TypeError, ValueError):
            return render_template("apology.html")

@app.route("/todaytimetable", methods=["GET", "POST"])
def todaytimetable():
    if request.method == "POST":
        address = request.form.get("kota")
        method = request.form.get("method")
        now = datetime.now()
        date = now.strftime("%d")
        year = now.strftime("%Y")
        month = now.strftime("%02m")
        monthname = now.strftime("%B")
        try:
            response = requests.get(f"https://api.aladhan.com/v1/calendarByAddress?address={urllib.parse.quote_plus(address)}&method={urllib.parse.quote_plus(method)}&month={urllib.parse.quote_plus(month)}&year={urllib.parse.quote_plus(year)}")
            response.raise_for_status()
        except requests.RequestException:
            return None
        # Parse response
        try:
            jd = response.json()["data"]
            n = int(date)
            fajr1 = int(jd[n-1]["timings"]["Fajr"][0:2])
            fajr2 = int(jd[n-1]["timings"]["Fajr"][3:5])
            zuhr1 = int(jd[n-1]["timings"]["Dhuhr"][0:2])
            zuhr2 = int(jd[n-1]["timings"]["Dhuhr"][3:5])
            asr1 = int(jd[n-1]["timings"]["Asr"][0:2])
            asr2 = int(jd[n-1]["timings"]["Asr"][3:5])
            magh1 = int(jd[n-1]["timings"]["Maghrib"][0:2])
            magh2 = int(jd[n-1]["timings"]["Maghrib"][3:5])
            isy1 = int(jd[n-1]["timings"]["Isha"][0:2])
            isy2 = int(jd[n-1]["timings"]["Isha"][3:5])
            method = jd[n-1]["meta"]["method"]["name"]
            return render_template("todaytimetable.html", method=method, date=date, fajr1=fajr1, fajr2=fajr2, zuhr1=zuhr1, zuhr2=zuhr2, asr1=asr1, asr2=asr2, magh1=magh1, magh2=magh2, isy1=isy1, isy2=isy2, monthname = monthname, year = year, address=address)
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
