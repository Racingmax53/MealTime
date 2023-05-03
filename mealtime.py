from flask import Flask, render_template, request, url_for, redirect, session
from pymongo.mongo_client import MongoClient
import sys

# print('This is error output', file=sys.stderr)
# print('This is standard output', file=sys.stdout)

uri = "mongodb+srv://gmaxgmiles:Qf2xJOsbIP9W8UxO@mealtime-db.sqseaxr.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

userDB = client["MealTime"]
mycol = userDB["users"]
loggedIn = False;
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Dummy Data


# myCredentials = { "username": "Max", 
#                 "password": "123" }

# ingredient1 = { "_id": 1,
#                 "name": "Tomato",
#                 "dietary": "",
#                 "unit": ""}

# ingredient2 = { "_id": 2,
#                 "name": "Egg",
#                 "dietary": "vegetarian",
#                 "unit": ""}

# ingredient3 = { "_id": 3,
#                 "name": "Salmon",
#                 "dietary": "pescatarian",
#                 "unit": "oz"}

# ingredient4 = { "_id": 4,
#                 "name": "Kale",
#                 "dietary": "vegan",
#                 "unit": "cup"}

# collection = userDB["Ingredients"]

# collection.insert_one(ingredient1)
# collection.insert_one(ingredient2)
# collection.insert_one(ingredient3)
# collection.insert_one(ingredient4)

# recipe1 = {
#         "_id": 10,
#         "title": "Tomato Salad",
#         "description": "A simple and refreshing salad that's perfect for summer.",
#         "ingredients": [
#         {
#             "name": "Tomato",
#             "quantity": 2,
#             "unit": "units"
#         },
#         {
#             "name": "Cucumber",
#             "quantity": 1,
#             "unit": "units"
#         },
#         {
#             "name": "Olive Oil",
#             "quantity": 1,
#             "unit": "tablespoon"
#         },
#         {
#             "name": "Balsamic Vinegar",
#             "quantity": 1,
#             "unit": "tablespoon"
#         }
#     ],
#     "instructions": [
#         "Slice the tomatoes and cucumber into bite-sized pieces.",
#         "Combine the olive oil and balsamic vinegar in a small bowl and whisk to combine.",
#         "Drizzle the dressing over the tomato and cucumber, tossing to coat.",
#         "Serve immediately."
#     ]
# }

# recipe2 = {
#     "_id": 11,
#     "title": "Chicken Alfredo",
#     "description": "A classic pasta dish that's creamy and comforting.",
#     "ingredients": [
#         {
#             "name": "Pasta",
#             "quantity": 8,
#             "unit": "ounces"
#         },
#         {
#             "name": "Chicken Breast",
#             "quantity": 2,
#             "unit": "units"
#         },
#         {
#             "name": "Heavy Cream",
#             "quantity": 1,
#             "unit": "cup"
#         },
#         {
#             "name": "Parmesan Cheese",
#             "quantity": 1,
#             "unit": "cup"
#         }
#     ],
#     "instructions": [
#         "Cook the pasta according to package instructions.",
#         "While the pasta cooks, season the chicken with salt and pepper and cook in a skillet over medium heat until no longer pink.",
#         "Remove the chicken from the skillet and set aside.",
#         "In the same skillet, add the heavy cream and Parmesan cheese, whisking constantly until the cheese is melted and the sauce is smooth.",
#         "Add the cooked chicken back to the skillet and toss to coat in the sauce.",
#         "Serve the chicken and sauce over the cooked pasta."
#     ]
# }

# collection = userDB["recipes"]

# collection.insert_one(recipe1)
# collection.insert_one(recipe2)


def checkCredentials(_fromDB, _username, _password):
    # Check if the password provided is correct
    if _password == _fromDB[0]["password"]:
        # If password is correct, proceed to user homepage
        # print("password correct", file=sys.stdout)
        return True
    else:
        # If password is incorrect, stay at login page
        # print("password incorrect", file=sys.stdout)
        return False


# @app.route('/')
# def home():
#     if 'logged_in' in session and session['logged_in']:
#         # User is logged in
#         return redirect(url_for("user", usr=user))
#     else:
#         # User is not logged in
#         return redirect(url_for("login"))

@app.route('/')
def home():
    collection = userDB["recipes"]
    recipes = collection.find()
    return render_template('home.html', recipes=recipes)



@app.route('/checkping')
def checkping(): 
    try:
        client.admin.command('ping')
        return 'Pinged your deployment. You successfully connected to MongoDB!'
    except Exception as e:
        return e

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form['button'] == 'Submit':
            print('Submit Pressed', file=sys.stdout)
            # Get data from Username text field
            user = request.form["username"]

            # Get data from Password text field
            password = request.form["password"]

            # Check if that Username exists in the DB
            nameQuery = { "username": user }
            mydoc = mycol.find(nameQuery)
            

            if checkCredentials(mydoc, user, password):
                session['logged_in'] = True
                return redirect(url_for("user", usr=user))
            else:
                return redirect(url_for("login"))  

        elif request.form['button'] == 'Create Account':
            return redirect(url_for("signup"))

        else:
            print("Bad parameter", file=sys.stdout)
    else:
        return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    return render_template("createacct.html")

@app.route("/recipes")
def recipes():
    return render_template("recipes.html")

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return redirect(url_for("recipes"))
    recipes = userDB.recipes.find({"title": {"$regex": query, "$options": "i"}})
    return render_template("recipes.html", recipes=recipes)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for("login"))

@app.route("/displayrecipe")
def displayrecipe():
    return render_template("displayrecipe.html", title="Test")


@app.route('/createrecipe', methods=['GET', 'POST'])
def show_createrecipe():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form['ingredients']
        steps = request.form['steps']

        # Store the recipe data in a database
        _recipe = {
            "_id": 1,
            "title": name,
            "description": description,
            "ingredients": ingredients,
            "instructions": steps
        }

        collection = userDB["recipes"]
        collection.insert_one(_recipe)

        return redirect(url_for('show_createrecipe'))

    return render_template('createrecipe.html')



class Recipe:
    def __init__(self, recipe_id, name, description, ingredients, steps):
        self.recipe_id = recipe_id
        self.name = name
        self.description = description
        self.ingredients = ingredients
        self.steps = steps

# route for displaying a recipe
@app.route('/displayrecipe/<int:recipe_id>')
def display_recipe(recipe_id):
    collection = userDB["recipes"]
    # retrieve the recipe from the database
    recipe = collection.find_one({'_id': recipe_id})

    # create a Recipe object
    name = recipe['title']
    description = recipe['description']
    ingredients = recipe['ingredients']
    steps = recipe['instructions']
    recipe_obj = Recipe(recipe_id, name, description, ingredients, steps)

    # pass the Recipe object to the template
    return render_template('displayrecipe.html', recipe=recipe_obj)

if __name__ == '__main__': 
    app.run(debug=True)
  


