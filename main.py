from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from replit import db
import secrets
import json
from datetime import datetime
from emailwork import sendemail
import pytz
import os
import time
from urlextract import URLExtract
import requests
from flask_socketio import SocketIO, send, join_room, leave_room
from math import factorial

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins='*')

activeUsers = []
userTimes = []


@app.route('/down')
def loginredirect():
  return render_template("down.html")


@app.route("/themes")
def themes():
  return render_template("themes.html")


@app.route("/test")
def emailtesting():
  message = request.args.get('message')
  sendemail("HADFIELD.Mitchell@mazenod.wa.edu.au", "yej", str(message), "")
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


@app.route('/factorial')
def factorials():
  num = request.args.get('num')
  return str(factorial(int(num)))

@app.route('/me', methods=['post'])
def whome():
  user = session['user']
  return user

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
      filename = "profile_default.jpg"
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


@app.errorhandler(500)
def baderror(e):
  print(
    rgbToAnsi(255, 0, 0,
              "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n" + str(e)))
  return render_template('500.html'), 500


@app.route("/causeerror")
def why():
  return noodles


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


def is_url_image(image_url):
  image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif",
                   "image/svg+xml")
  r = requests.head(image_url)
  if r.headers["content-type"] in image_formats:
    return True
  return False


@app.route("/chat", methods=["POST", "GET"])
def chat():
  #return render_template('down.html')
  if request.method == "POST":
    user = session["user"]
    mxg = request.form["mxg"]
    extractor = URLExtract()
    urls = extractor.find_urls(mxg)
    for url in urls:
      ogurl = url
      if not ("http://" in url or "https://" in url):
        url = "<a href='https://" + url + "'>https://" + url + "</a>"
      else:
        url = "<a href='" + url + "'>" + url + "</a>"
      try:
        if not ("http://" in ogurl or "https://" in ogurl):
          ogurl = "https://" + ogurl
        if is_url_image(ogurl):
          url = "<img style='max-width: 200px; max-height: 200px;' src='" + ogurl + "'>"
          # wow that actually worked
      except:
        pass
      mxg = mxg.replace(ogurl, url)
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
    return "OK"
  else:
    if "user" in session:
      user = session["user"]
      with open("chat.json", 'r') as file:
        messages = json.load(file)
      try:
        loadAll = bool(request.args.get("loadAll"))
      except:
        loadAll = False
      return render_template("chat.html", user=user, hist=messages)
    else:
      flash("You need to be logged in to use chat!")
      return redirect(url_for("login"))


@socketio.on('message')
def handle_message(idk, message):
    print("socket tej")
    mxg = message
    extractor = URLExtract()
    urls = extractor.find_urls(mxg)
    for url in urls:
      ogurl = url
      if not ("http://" in url or "https://" in url):
        url = "<a href='https://" + url + "'>https://" + url + "</a>"
      else:
        url = "<a href='" + url + "'>" + url + "</a>"
      try:
        if not ("http://" in ogurl or "https://" in ogurl):
          ogurl = "https://" + ogurl
        if is_url_image(ogurl):
          url = "<img style='max-width: 200px; max-height: 200px;' src='" + ogurl + "'>"
          # wow that actually worked
      except:
        pass
      mxg = mxg.replace(ogurl, url) 
    user = session["user"]
    print(user)
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
    message = chatdict[current_key]
    send(message, broadcast=True)

online = []


def rgbToAnsi(r, g, b, text):
  return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

@app.route('/chat/userrefresh')
def chatuserrefresh():
  data = {}
  data["online"] = {}
  data["offline"] = {}

  with open("users.json", 'r') as f:
    userdict = json.load(f)
    f.close()

  for child, item in enumerate(activeUsers):
    containing_key = find_parent_key_containing_value(userdict, item)
    data["online"][child] = {}
    data["online"][child]["author"] = item
    try:
      print(containing_key)
      data["online"][child]["profile"] = userdict[containing_key]["profile"]
    except Exception as e:
      print(e)
      data["online"][child]["profile"] = "profile_default.jpg"

  with open("users.json", 'r') as f:
    userdict = json.load(f)
    f.close()

  childrenkeys = []

  for child in userdict.keys():
    childrenkeys.append(child)

  for child, key in enumerate(childrenkeys):
    username = userdict[key]['username']
    profile = userdict[key]['profile']

    data["offline"][child] = {}
    data["offline"][child]["author"] = username
    try:
      data["offline"][child]["profile"] = profile
    except:
      data["offline"][child]["profile"] = "profile_default.jpg"

  return jsonify(data)


@app.route("/changelog")
def changelog():
  return """
  <h4>Changelog</h4>
  <p>v1.0.1 - Bot functionality</p>
  <p>v1.0.0 - It now is an actual chat</p>
  """
  
@app.route('/prefrences')
def prefrences():
  if "user" in session:
    user = session["user"]
    return render_template("pref.html", children="one")
  else:
    flash("You need to be logged in to use chat!")
    return redirect(url_for("login"))


@app.route("/prefrences/avatar", methods=["POST", "GET"])
def change_avatar():
  if request.method == "POST":
    profile_image = request.files["profile_image"]
    user = session["user"]
    with open("users.json", 'r') as file:
      udic = json.load(file)
    parent_key = find_parent_key_containing_value(udic, user)
    men = udic[parent_key]['profile']
    if men == "profile_default.jpg":
      with open("misc.json", 'r') as file:
        misc = json.load(file)
      misc['profilecount'] += 1
      filename = f"profile_{misc['profilecount']}.png"
      with open("misc.json", 'w') as file:
        json.dump(misc, file)
    else:
      filename = men
    file_path = os.path.join('static', 'images', filename)
    profile_image.save(file_path)
    udic[parent_key]["profile"] = filename
    with open("users.json", 'w') as file:
      json.dump(udic, file)
    flash("Changes successful, will be enacted from your next post")
    return redirect(url_for("prefrences"))
  else:
    if "user" in session:
      user = session["user"]
      return render_template("pref.html", children="two")
    else:
      flash("You need to be logged in to use chat!")
      return redirect(url_for("login"))


@app.route("/prefrences/somethingelse")
def change_something():
  if "user" in session:
    user = session["user"]
    return "bruh"
    #return render_template("pref.html", children="two")
  else:
    flash("You need to be logged in to use chat!")
    return redirect(url_for("login"))


@app.route('/api/bot/send_message')  # can we join vc real quick ; ok
def bot_send():
  with open("chat.json", 'r') as file:
    chatdict = json.load(file)
  with open("misc.json", 'r') as file:
    misc = json.load(file)
  token = request.args.get('token')
  mxg = request.args.get('message')
  user = misc[token]["username"]
  max_key = max(map(int, chatdict.keys()))
  current_key = max_key + 1
  current_key = str(current_key)
  auzTime = pytz.timezone('Australia/Perth')
  msgtime = datetime.now(auzTime).strftime('%I:%M %p')
  chatdict[current_key] = {}
  chatdict[current_key]["author"] = user
  chatdict[current_key]["message"] = mxg
  chatdict[current_key]["time"] = msgtime
  chatdict[current_key]["profile"] = misc[token]["profile"]
  with open("chat.json", 'w') as file:
    json.dump(chatdict, file)
  return "200"


@app.route('/api/bot/check_messages')
def bot_read():
  token = request.args.get('token')
  with open('chat.json', 'r') as f:
    messages = json.load(f)
    f.close()
  with open('misc.json', 'r') as f:
    misc = json.load(f)
    f.close()
  if token in misc:
    return jsonify(messages)
  else:
    return "error (403)"


@app.route('/dbottoken')
def yejis():
  with open("misc.json", 'r') as file:
    misc = json.load(file)
    misc["key_savagelemon"] = {}
    misc["key_savagelemon"]["username"] = "Savage Lemon (Bot)"
    misc["key_savagelemon"]["profile"] = "profile_bot_1.png"
    with open("misc.json", 'w') as file:
      json.dump(misc, file)
    return "m"


socketio.run(app, host='0.0.0.0', port=81)
