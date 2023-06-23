from flask import Flask, render_template, request, url_for, redirect, session
from pymongo.mongo_client import MongoClient
import sys, random, requests

# Constants
URI                 = "mongodb+srv://gmaxgmiles:Qf2xJOsbIP9W8UxO@mealtime-db.sqseaxr.mongodb.net/?retryWrites=true&w=majority"
APIKEY              = 'c3a2c84bdd684a61b2c9611f766fa65c'
APISEARCHQ          = 'https://api.spoonacular.com/recipes/complexSearch?apiKey=' + APIKEY + '?query='
APISEARCHD          = 'https://api.spoonacular.com/recipes/complexSearch?apiKey=' + APIKEY + '&dietary='
APIGET              = ['https://api.spoonacular.com/recipes/', '/information?apiKey=' + APIKEY]


# Create a new client and connect to the server
client = MongoClient(URI)
userDB = client["MealTime"]
mycol = userDB["users"]
loggedIn = False;
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
collection_mealplan = userDB["mealplan"]
dummy_mealplan = [None] * 21

global userPref, ingredientListID, mealPlan, ingredientList, nextIngredientID, nextRecipeID, nextUserID
userPref = 'none'
dieteryprefs = ['none', 'vegetarian', 'pescatarian'] 
ingredentList = []

nextIngredientID = int(0)
nextRecipeID = int(0)
nextUserID = int(0)


class Recipe:
    def __init__(self, recipe_id, name, description, ingredients, steps, pref):
        self.recipe_id = recipe_id
        self.name = name
        self.description = description
        self.ingredients = ingredients
        self.steps = steps
        self.pref = pref

class User:
    def __init__(self, _user_id, _name, _password, _mealplan, _pref):
        self.user_id = _user_id
        self.name = _name
        self.password = _password
        self.mealplan = _mealplan
        self.pref = _pref

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
    collection = userDB["recipes"]
    randomRecipes = collection.aggregate([
        { "$match": {"dietary": userPref} },
        { "$sample": { "size": 21 } }
    ])

    toReturn = []

    for meal in randomRecipes:
        toReturn.append(meal)

    while toReturn.__len__() < 21:
        index = random.randint(0, toReturn.__len__() - 1)
        toReturn.append(toReturn[index])
    
    return toReturn

def generateMealPlanWithAPI():
    global userPref
    totalEntries = getRecipeByDietary(userPref).get('results')
    print(type(totalEntries))
    return random.choices(totalEntries, k=21)


def createUser(_name, _password, _mealplan, _pref):
    global nextUserID
    collection = userDB["users"]

    if (collection.count_documents({}) < 1):
        # print('empty user collection', file=sys.stdout)
        nextUserID = 1
        firstUser = User(nextUserID, _name, _password, dummy_mealplan, _pref)
    
    else: 
        nextUserID = collection.find().sort("_id", -1).limit(1)[0]["_id"] + 1
        
    _user = {
            "_id": nextUserID,
            "name": _name,
            "password": _password,
            "mealplan": dummy_mealplan,
            "dietary": _pref,
        }
    collection.insert_one(_user)
    
    # highestID = userDB.collection.find().sort({":_id": -1}).limit(1)


def getRecipeByKeyword(_keyword):
    return requests.get(APISEARCHQ + _keyword + '&number=1').json()


def getRecipeByDietary(_dietary):
    # toReturn = []

    # breakfast_options   = requests.get(APISEARCHD + _dietary + '&number=100&type=breakfast').json()
    # lunch_options       = requests.get(APISEARCHD + _dietary + '&number=100&type=breakfast').json()
    # dinner_options      = requests.get(APISEARCHD + _dietary + '&number=100&type=breakfast').json()

    # toReturn.append(breakfast_options.get('results'))
    # toReturn.append(lunch_options.get('results'))
    # toReturn.append(dinner_options.get('results'))
    # return toReturn
    return requests.get(APISEARCHD + _dietary + '&number=250').json()


def getRecipeDetails(_recipeID):
    # Search by Recipe ID
    # '782585' = Recipe ID
    # response = requests.get(APIGET[0] + '782585' + APIGET[1])
    details_results = requests.get(APIGET[0] + str(_recipeID) + APIGET[1])
    details_results = details_results.json()
    del details_results['veryHealthy']
    del details_results['cheap']
    del details_results['veryPopular']
    del details_results['sustainable']
    del details_results['lowFodmap']
    del details_results['weightWatcherSmartPoints']
    del details_results['gaps']
    del details_results['preparationMinutes']
    del details_results['cookingMinutes']
    del details_results['healthScore']
    del details_results['creditsText']
    del details_results['sourceName']
    del details_results['pricePerServing']
    del details_results['readyInMinutes']
    del details_results['image']
    del details_results['imageType']
    del details_results['occasions']
    del details_results['winePairing']
    del details_results['analyzedInstructions']
    del details_results['spoonacularSourceUrl']
    return details_results


# Helper function to check what the last recipe ID was and add one
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


# Helper method to check what the dietary restrictions are of the passed in variable
def checkDietary(_ingredient):
    toReturn = 'none'

    if (_ingredient[0]['dietary'] == ''):                    
        print('none', file=sys.stdout)

    elif (_ingredient[0]['dietary'] == 'vegetarian'):
        if (toReturn == 'none'):
            toReturn = 'vegetarian'                    
            # print('vegetarian', file=sys.stdout)

    elif (_ingredient[0]['dietary'] == 'pescatarian'):
        if (toReturn == 'none' or toReturn == 'vegetarian'):
            toReturn = 'pescatarian'
            # print('pescatarian', file=sys.stdout)

    return toReturn


# Helper method to compile how much of each ingredient is needed
def getIngredients():
    toReturn = []

    return toReturn


@app.route('/')
def home():
    global mealPlan
    mealPlan = dummy_mealplan

    return render_template('home.html')

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
    global mealPlan
    user = userDB["users"].find_one( {"_id": 1} )
    mealPlan = user["mealplan"]

    if request.method == 'POST':
        mealPlan = generateMealPlan()
        userDB["users"].update_one( {"_id": 1} , { "$set": { 'mealplan': mealPlan } })


    return render_template("mealplan.html", _mealplan = mealPlan)

@app.route("/mealplanapi", methods=['GET', 'POST'])
def mealplanapi():
    global mealPlan
    # user = userDB["users"].find_one( {"_id": 1} )
    # mealPlan = user["mealplan"]
    mealPlan = dummy_mealplan

    if request.method == 'POST':
        mealPlan = generateMealPlanWithAPI()
        return render_template("mealplanapi.html", mealplan = mealPlan)

    return render_template("mealplanapi.html", mealplan = mealPlan)

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

        # If each ingredient element contains 2 elements there is no unit, if 3 there is a unit
        for ingredient in ingredientList:
            subIngredient = ingredient.split('-')

            if (len(subIngredient) == 2): # No units provided

                # Check if ingredient already exists in the DB
                foundIngredient = collection.find({"name": subIngredient[1]})

                # If ingredient is in the DB, store quantity and ingredient ID
                ingredientListID.append([int(subIngredient[0]), foundIngredient[0]['_id']])

                dietary_raw = checkDietary(foundIngredient)


            
            elif (len(subIngredient) == 3): # Units provided
                # Check if ingredient already exists in the DB
                foundIngredient = collection.find({"name": subIngredient[2]})

                # If ingredient is in the DB, store quantity and ingredient ID
                ingredientListID.append([int(subIngredient[0]), foundIngredient[0]['_id']])

                dietary_raw = checkDietary(ingredient)
        
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

@app.route("/shoppinglist")
def shoppinglist():

    return render_template("shoppinglist.html")

if __name__ == '__main__': 
    app.run(debug=True)
  


# @app.route('/')
# def home():
#     if 'logged_in' in session and session['logged_in']:
#         # User is logged in
#         return redirect(url_for("user", usr=user))
#     else:
#         # User is not logged in
#         return redirect(url_for("login"))