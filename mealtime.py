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


mydict = { "username": "Max", "password": "123" }

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


@app.route('/')
def home():
    if 'logged_in' in session and session['logged_in']:
        # User is logged in
        return redirect(url_for("user", usr=user))
    else:
        # User is not logged in
        return redirect(url_for("login"))


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

@app.route("/<usr>")
def user(usr):
    return render_template("home.html", username=usr)

@app.route("/recipes")
def recipes():
    return render_template("recipes.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for("login"))

@app.route("/displayrecipe")
def displayrecipe():
    return render_template("displayrecipe.html", title="Test")

if __name__ == '__main__': 
    app.run(debug=True)
  


