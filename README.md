# daily-meal-tracker

Project name: Foodie, daily meal tracker

overview: The goal of the project was to build a website which is an online meal tracker where you can search
          for food, add them to your daily meals and track how many calories you ate for each meal
          as well as for each day.
          the project is dependent on Edamam API which is a food database API that is used to search
          for different types of food using their name and getting back different nutritional information
          about each of them, The API is used in the project for searching their database using a food name
          and getting the amount of calories, protien and carbs for each food item using the specified measures
          for each food.

Functions:

    1- Searching: The website allows users to search for food names, see the different results and view
                  the nutritional information for each item without the need of registration but they
                  won't be able to add the food to their daily dairy or count their calories.

    2- Registration: The website has forms for creating an account and logging in which it gives the users
                     the searching functionality as well as allowing them to add food into their diary
                     and calculate their calories.

    3- Dashboard: Each user has their own dashboard where they are able to view the food items that they
                  have added to each meal and the amount of calories for the day and for each meal.

Database:

    1- users: The first table in the database which contains the user information that include: user_id,
              username, email, password_hash.

    2- food_diary: this table conatins all the food items that where saved by different users for their
                   dashboard and that includes: diary_id, user_id, food_id, food_name, serving_size
                   (the measuring unit, whether gram,kilogram,ounce,etc.), no_of_servings, calories,
                   category(whether breakfast, lunch, dinner or snacks) and date_added.
