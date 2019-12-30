import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from helpers import login_required, lookup, getnutrients
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")

# Make sure API key is set
if not os.environ.get("APP_KEY") or not os.environ.get("APP_ID"):
    raise RuntimeError("APP_KEY and/or APP_ID are not set")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        foodname = request.form.get('search-field')
        foods, nextlink = lookup(foodname)
        return render_template("search-result.html", foods=foods, nextlink=nextlink, foodname=foodname)
    else:
        return render_template("index.html")

@app.route("/search-result")
def searchResult():
    return render_template("search-result.html")

@app.route("/food-display")
def displayFood():
    foodid = request.args.get('food')
    food = lookup(foodid)
    return render_template("food-display.html", food=food[0])

@app.route("/getNutrients")
def getNutrients():
    measureuri = request.args.get("measureuri")
    qualifyuri = request.args.get("qualifyuri")
    foodid = request.args.get("foodid")
    quantity = request.args.get("quantity")
    print(measureuri)
    print(qualifyuri)
    print(foodid)
    nutrition = getnutrients(measureuri, qualifyuri, foodid, quantity)
    print(nutrition)
    return jsonify(nutrition)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("password_confirm")

        print(email)

        if not username:
            flash("must provide username")
            return redirect("/register")
        elif not email:
            flash("must provide an email")
            return redirect("/register")
        elif not password:
            flash("must provide password")
            return redirect("/register")
        elif not confirm_password or password != confirm_password:
            flash("your passwords don't match")
            return redirect("/register")

        email_exist = db.execute("SELECT user_id FROM users WHERE email=:email", email=email)
        if len(email_exist) != 0:
            flash("User already exists")
            return redirect("/register")

        hashed = generate_password_hash(password)
        result = db.execute("INSERT INTO users (email, username, password_hash) VALUES (:email, :username, :hashed)", email=email, username=username, hashed=hashed)

        if not result:
            flash("user already exists")
            return redirect("/register")

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["user_id"]

        flash("Welcome! You have created your account")
        return redirect("/")
    else:
        nav_flag = 1
        return render_template("register.html", nav_flag=nav_flag)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("must provide an email")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("passwordLogin"):
            flash("must provide a password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("passwordLogin")):
            flash("invalid email and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        flash("Welcome back!")
        return redirect("/")
    else:
        nav_flag = 1
        return render_template("login.html", nav_flag=nav_flag)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/addfood", methods=["POST"])
@login_required
def addfood():
    foodid = request.form.get("foodid")
    foodname = request.form.get("foodname")
    serving_amount = request.form.get("servingamount")
    serving_size = request.form.get("servingsize")
    calories = request.form.get("caloriesmodal")
    category = request.form.get("categoryselect")
    date = request.form.get("datepicker")
    date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    print(date)
    today = datetime.date.today()
    print(today)
    if not serving_size or serving_size == "choose a serving size":
        flash("Please choose a serving size")
        return redirect(url_for('displayFood', food=foodid, **request.args))
    if not category or category == "Choose a category":
        flash("Please choose a category")
        return redirect(url_for('displayFood', food=foodid, **request.args))

    if today != date:
        result = db.execute("INSERT INTO food_diary (user_id, food_id, food_name, serving_size, no_of_servings, calories, category, date_added) VALUES (:userid, :foodid, :foodname, :serving_size, :serving_amount, :calories, :category, :date)",
                            userid=session["user_id"], foodid=foodid, foodname=foodname, serving_size=serving_size, serving_amount=serving_amount, calories=calories, category=category, date=date)
    else:
        result = db.execute("INSERT INTO food_diary (user_id, food_id, food_name, serving_size, no_of_servings, calories, category) VALUES (:userid, :foodid, :foodname, :serving_size, :serving_amount, :calories, :category)",
                            userid=session["user_id"], foodid=foodid, foodname=foodname, serving_size=serving_size, serving_amount=serving_amount, calories=calories, category=category)

    if result:
        flash("Food item added!")
        return redirect("/dashboard")
    else:
        return redirect("/")

@app.route("/getFoodDiary", methods=["GET"])
@login_required
def getFoodDiary():
    date = request.args.get("date")
    user_id = session["user_id"]
    print(date)
    date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    print(date)

    rows = db.execute("SELECT diary_id, food_id, food_name, serving_size, no_of_servings, calories, category FROM food_diary WHERE user_id=:user_id AND date_added=:date",
           user_id=user_id, date=date)

    if rows:
        return(jsonify(rows))
    else:
        return(jsonify(False))