import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(food):
    """Look up quote for symbol."""

    # Contact API
    try:
        app_key = os.environ.get("APP_KEY")
        app_id = os.environ.get("APP_ID")
        response = requests.get(f"https://api.edamam.com/api/food-database/parser?ingr={urllib.parse.quote_plus(food)}&app_id={app_id}&app_key={app_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

# Parse response
    try:
        foods = response.json()
        hints = foods['hints']
        try:
            nextlink = foods['_links']['next']['href']
            return hints, nextlink
        except:
            return hints
    except (KeyError, TypeError, ValueError):
        return None

def getnutrients(measureuri, qualifyuri, foodid, quantity):
     # Contact API
    print("################### quantity: ", quantity)
    if not qualifyuri:
        try:
            app_key = os.environ.get("APP_KEY")
            app_id = os.environ.get("APP_ID")
            response = requests.post(f"https://api.edamam.com/api/food-database/nutrients?app_id={app_id}&app_key={app_key}",
                        json={"ingredients": [{"quantity": int(quantity), "measureURI": measureuri, "foodId": foodid}]})
            response.raise_for_status()
        except requests.RequestException:
            return None
    else:
        try:
            app_key = os.environ.get("APP_KEY")
            app_id = os.environ.get("APP_ID")
            response = requests.post(f"https://api.edamam.com/api/food-database/nutrients?app_id={app_id}&app_key={app_key}",
                        json={"ingredients": [{"quantity": int(quantity), "measureURI": measureuri, "foodId": foodid, "qualifiers": [qualifyuri]}]})
            response.raise_for_status()
        except requests.RequestException:
            return None

# Parse response
    try:
        food = response.json()
        print(food)
        try :
            calories = food['calories']
        except:
            calories = 0
        try:
            weight = food['totalWeight']
        except:
            weight = 0
        nutrients = food['totalNutrients']
        try:
            fat = nutrients['FAT']['quantity']
        except:
            fat = 0
        try:
            carbs = nutrients['CHOCDF']['quantity']
        except:
            carbs = 0
        try:
            protein = nutrients['PROCNT']['quantity']
        except:
            protein = 0
        return {
            "foodid": food['ingredients'][0]['parsed'][0]['foodId'],
            "foodname": food['ingredients'][0]['parsed'][0]['food'],
            "calories": int(calories),
            "weight": int(weight),
            "fat": int(fat),
            "carbs": int(carbs),
            "protein": int(protein)
        }

    except (KeyError, TypeError, ValueError):
        return None