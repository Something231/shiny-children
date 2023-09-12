from flask import Flask, render_template, request, redirect, url_for, session, flash
from replit import db
import secrets
import json
from datetime import datetime
from emailwork import sendemail
import pytz
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/images'

@app.route('/login')
def loginredirect():
  return redirect(url_for("login"))

@app.route("/test")
def emailtesting():
  sendemail("BRIGGS.Hamish@mazenod.wa.edu.au", "Please verify your email",
            "We need to verify your email so you can sign up for e",
            "Verify at https://e.captaindeathead.repl.co/verify/e")
  return "might have worked"


@app.route('/', methods=["POST", "GET"])
def login():
  # oh my god thanks hamish, i hate doing logins, do register as well and ill give you a service medal
  if request.method == "POST":  #theres a few things i need to change
    user = request.form["nm"]
    user = user.lower()
    if user in db:
      password = request.form["pcode"]
      if db[user] == [password]:
        with open("users.json", 'r') as file:
          userdict = json.load(file)
        try:
          men = userdict[user]["username"]
          session["user"] = men
        except Exception as e:
          session["user"] = user
          print(e)
        flash("Login successful")
        return redirect(url_for("landing"))
      else:
        flash("Incorrect username or password")
        return redirect(url_for("login"))
    else:
      flash("Incorrect username or password")
      return redirect(url_for("login"))
  else:
    if "user" in session:
      flash("Already logged in!")
      return redirect(url_for("landing"))
    return render_template("login.html")


@app.route("/home")
def unstableplazma():
  return "This page doesn't exist yet, please go back"


@app.route("/register", methods=["POST", "GET"])
def register():
  if request.method == "POST":
    user = request.form["nm"]
    user = user.lower()
    if user in db:
      flash("Account already exists!")
      return redirect(url_for('register'))
    password = request.form["pcode"]
    newusername = request.form["uname"]
    newusername = newusername.lower()
    db[user] = [password]
    with open("misc.json", 'r') as file:
      misc = json.load(file)
    if "profilecount" not in misc:
      misc["profilecount"] = 0
    misc['profilecount'] += 1  # are you happy with the nw look????????? thanks
    profile_image = request.files["profile_image"]  #lemme chek Its very nice
    if profile_image:
      filename = f"profile_{misc['profilecount']}.png"
      file_path = os.path.join('static', 'images', filename)
      profile_image.save(file_path)
    else:
      filename = "profile_default.png"
    with open("users.json", 'r') as file:
      userdict = json.load(file)
    userdict[user] = {}
    userdict[user]["username"] = newusername
    userdict[user]["profile"] = filename
    with open("misc.json", 'w') as file:
      json.dump(misc, file)
    with open("users.json", 'w') as file:
      json.dump(userdict, file)
    session["user"] = newusername
    return redirect(url_for("landing"))
  else:
    if "user" in session:
      flash("Already Logged in!")
      return redirect(url_for("landing"))
    return render_template("register.html")


@app.route("/logout")
def logout():
  if "user" in session:
    user = session["user"]
    flash(f"You have been logged out, {user}", "info")
  else:
    flash("You are not logged in!")
  session.pop("user", None)
  return redirect(url_for("login"))


@app.route("/landing")
def landing():
  if "user" in session:
    user = session["user"]
    return render_template("landing.html", user=user)
  else:
    flash("You are not logged in!")
    return redirect(url_for("login"))


@app.route("/home")
def homeredirect():
  return redirect(url_for('index'))


#im doing backend or fronKend?.> both i guess
#ok ill exist


def write_to_json(data, filename):
  with open(filename, 'r+') as file:
    messages = json.load(file)
    messages.append(data)
    file.seek(0)
    json.dump(messages, file, indent=4)
    file.truncate()


def read_from_json(filename):
  with open(filename, 'r') as file:
    messages = json.load(file)
  contents = [message['content'] for message in messages]
  return contents


@app.errorhandler(404)
def error(e):
  return render_template('404.html')

def find_parent_key_containing_value(d, target_value):
    for key, value in d.items():
        if isinstance(value, dict):
            if target_value in value.values():
                return key
            else:
                parent_key = find_parent_key_containing_value(value, target_value)
                if parent_key:
                    return parent_key
    return None
  
@app.route("/chat", methods=["POST", "GET"])
def chat():
  if request.method == "POST":
    user = session["user"]
    mxg = request.form["mxg"]
    auzTime = pytz.timezone('Australia/Perth')
    # niceAuzTime converts to 12 hour time with AM/PM
    msgtime = datetime.now(auzTime).strftime('%I:%M %p')
    with open("chat.json", 'r') as file:
      chatdict = json.load(file)
    if not chatdict:
      chatdict = {}
    if chatdict != {}:
      max_key = max(map(int, chatdict.keys()))
      current_key = max_key + 1
    else:
      current_key = 0
    with open("users.json", 'r') as file:
      userdict = json.load(file) 
    containing_key = find_parent_key_containing_value(userdict, user)
    current_key = str(current_key)
    chatdict[current_key] = {}
    chatdict[current_key]["author"] = user
    chatdict[current_key]["message"] = mxg
    chatdict[current_key]["time"] = msgtime
    try:
      print(containing_key)
      chatdict[current_key]["profile"] = userdict[containing_key]["profile"]
    except Exception as e:
      print(e)
      chatdict[current_key]["profile"] = "profile_default.jpg"
    with open("chat.json", 'w') as file:
      json.dump(chatdict, file)
    return redirect(url_for("chat"))
  else:
    if "user" in session:
      user = session["user"]
      with open("chat.json", 'r') as file:
        messages = json.load(file)
      return render_template("chat.html", user=user, hist=messages)
    else:
      flash("You need to be logged in to use chat!")
      return redirect(url_for("login"))


#@app.route("/keym")
#def keym():
 # keys = db.keys()
  #return str(keys)
  # nah im back

@app.route('/chat/refresh')
def chatrefresh():
    with open('chat.json', 'r') as f:
        messages = json.load(f)
        f.close()
    return messages

@app.route("/changelog")
def changelog():
  return """
  Changelog
  v1.0.0 - It now is an actual chat
  """

app.run(host='0.0.0.0', port=81)
