from flask import Flask, render_template, request, url_for, redirect, session
from pymongo.mongo_client import MongoClient
import sys, random

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

collection_mealplan = userDB["mealplan"]

dummy_mealplan = [None] * 21


dieteryprefs = ['none', 'vegetarian', 'pescatarian']
global userPref 
userPref = 'none'

global nextRecipeID, nextIngredientID, ingredientListID
nextIngredientID = int(0)
nextRecipeID = int(0)

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
    
def generateMealPlan():
    global userPref
    
    toReturn = [None] * 21

    collection = userDB["recipes"]
    recipes = collection.find({"dietary": userPref})

    print(recipes, file=sys.stdout)
    # toReturn = random.sample(recipes["_id"], 21)

    return toReturn


def getNextRecipeID():
    global nextRecipeID
    toReturn = 0

    collection = userDB["recipes"]
    for x in collection.find({},{ "_id": 1}):
        # print(x["_id"], file=sys.stdout)
        if x["_id"] > toReturn:
            toReturn = x["_id"]

    # print(toReturn, file=sys.stdout)
    return toReturn + 1


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

@app.route("/mealplan", methods=['GET', 'POST'])
def mealplan():
    if request.method == 'POST':
        # print('testing', file=sys.stdout)
        generateMealPlan()

    return render_template("mealplan.html", _mealplan = dummy_mealplan)

@app.route('/createrecipe', methods=['GET', 'POST'])
def show_createrecipe():
    if request.method == 'POST':
        # Which DB queries to recipe collection
        collection = userDB["ingredients"]

        # Name of the recipe
        name_raw = request.form['name']

        # Description of the recipe
        description_raw = request.form['description']

        # String of all quantities, units, and ingredients used seperated by a comma
        ingredients_raw = request.form['ingredients']

        # Ingredient list with ingredient ID's and not names
        ingredientListID = []

        # Dietary Preference of the recipe
        dietary_raw = 'none'

        # Break ingredient string into a list of each comma section
        # Format QUANTITY-UNIT-INGREDIENT or QUANTITY-INGREDIENT
        ingredientList = ingredients_raw.split(',') 

        # Current ingredients in the DB
        currentIngredients = collection.find()

        # If each ingredient element contains 2 elements there is no unit, if 3 there is a unit
        for ingredient in ingredientList:
            subIngredient = ingredient.split('-')

            if (len(subIngredient) == 2): # No units provided
                # Check if ingredient already exists in the DB
                foundIngredient = collection.find({"name": subIngredient[1]})

                # If ingredient is in the DB, store quantity and ingredient ID
                ingredientListID.append([int(subIngredient[0]), foundIngredient[0]['_id']])
            
            elif (len(subIngredient) == 3): # Units provided
                # Check if ingredient already exists in the DB
                foundIngredient = collection.find({"name": subIngredient[2]})

                # If ingredient is in the DB, store quantity and ingredient ID
                ingredientListID.append([int(subIngredient[0]), foundIngredient[0]['_id']])

                if (foundIngredient[0]['dietary'] == ''):                    
                    print('none', file=sys.stdout)

                elif (foundIngredient[0]['dietary'] == 'vegetarian'):
                    if (dietary_raw == 'none'):
                        dietary_raw = 'vegetarian'                    
                    # print('vegetarian', file=sys.stdout)

                elif (foundIngredient[0]['dietary'] == 'pescatarian'):
                    if (dietary_raw == 'none' or dietary_raw == 'vegetarian'):
                        dietary_raw = 'pescatarian'
                    # print('pescatarian', file=sys.stdout)
        
            else: 
                print("didnt find item", file=sys.stdout)

        # print(ingredientListID, file=sys.stdout)
        steps_raw = request.form['steps']


        nextRecipeID = getNextRecipeID()

        # Store the recipe data in a database
        _recipe = {
            "_id": nextRecipeID,
            "title": name_raw,
            "description": description_raw,
            "ingredients": ingredientListID,
            "instructions": steps_raw,
            "dietary": dietary_raw,
        }

        # nextRecipeID = nextRecipeID + 1
        collection = userDB["recipes"]
        collection.insert_one(_recipe)
        # return render_template('/displayrecipe/' + str(nextRecipeID))
        # except:
        #     print("Error occurred while trying to push new recipe into the DB") 
        #     return render_template('createrecipe.html')
        
    return render_template('createrecipe.html')

@app.route('/preferences', methods=['POST', 'GET'])
def preferences():
    global userPref

    if request.method == "POST":
        if request.form['button'] == 'Submit':
            # print(request.form['user_pref'], file=sys.stdout)
            userPref = request.form['user_pref']
            # userPref = 'veg'
            # print(userPref, file=sys.stdout)

    
    return render_template('preferences.html', prefs=dieteryprefs)

class Recipe:
    def __init__(self, recipe_id, name, description, ingredients, steps, pref):
        self.recipe_id = recipe_id
        self.name = name
        self.description = description
        self.ingredients = ingredients
        self.steps = steps
        self.pref = pref

# route for displaying a recipe
@app.route('/displayrecipe/<int:recipe_id>')
def display_recipe(recipe_id):
    collection_recipe = userDB["recipes"]
    collection_ingredient = userDB["ingredients"]
    # retrieve the recipe from the database
    recipe = collection_recipe.find_one({'_id': recipe_id})

    # create a Recipe object
    name = recipe['title']
    description = recipe['description']
    steps = recipe['instructions']

    ingredients_raw = recipe['ingredients']
    ingredients = []

    pref = recipe['dietary']

    for ingredient in ingredients_raw:
        fromDB = collection_ingredient.find_one({"_id":ingredient[1]})
        temp_quantity = ingredient[0]
        temp_unit = fromDB["unit"]
        temp_name = fromDB["name"]
        temp = [temp_quantity, temp_unit, temp_name]
        # print(temp, file=sys.stdout)

        ingredients.append(temp)
        
    recipe_obj = Recipe(recipe_id, name, description, ingredients, steps, pref)

    # pass the Recipe object to the template
    return render_template('displayrecipe.html', recipe=recipe_obj)

if __name__ == '__main__': 
    app.run(debug=True)
  
# Dummy Data



# myCredentials = { "username": "Max", 
#                 "password": "123" }

# ingredient0 = { "_id": 0,
#                 "name": "ingredient0",
#                 "dietary": "",
#                 "unit": ""}

# ingredient1 = { "_id": 1,
#                 "name": "ingredient1",
#                 "dietary": "",
#                 "unit": ""}

# ingredient2 = { "_id": 2,
#                 "name": "ingredient2",
#                 "dietary": "vegetarian",
#                 "unit": ""}

# ingredient3 = { "_id": 3,
#                 "name": "ingredient3",
#                 "dietary": "pescatarian",
#                 "unit": "oz"}

# ingredient4 = { "_id": 4,
#                 "name": "ingredient4",
#                 "dietary": "vegan",
#                 "unit": "cup"}

# ingredient5 = { "_id": 5,
#                 "name": "ingredient5",
#                 "dietary": "vegetarian",
#                 "unit": ""}

# ingredient6 = { "_id": 6,
#                 "name": "ingredient6",
#                 "dietary": "pescatarian",
#                 "unit": "oz"}

# ingredient7 = { "_id": 7,
#                 "name": "ingredient7",
#                 "dietary": "vegan",
#                 "unit": "cup"}

# ingredient8 = { "_id": 8,
#                 "name": "ingredient8",
#                 "dietary": "",
#                 "unit": "oz"}

# ingredient9 = { "_id": 9,
#                 "name": "ingredient9",
#                 "dietary": "",
#                 "unit": "cup"}


# collection = userDB["ingredients"]

# collection.insert_one(ingredient0)
# collection.insert_one(ingredient1)
# collection.insert_one(ingredient2)
# collection.insert_one(ingredient3)
# collection.insert_one(ingredient4)
# collection.insert_one(ingredient5)
# collection.insert_one(ingredient6)
# collection.insert_one(ingredient7)
# collection.insert_one(ingredient8)
# collection.insert_one(ingredient9)