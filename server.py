
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = 'cs4111'


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://yz3323:170761@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()
# this create a new table
# conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );"""))
# conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

# conn.commit() 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query 
  #
  # cursor = g.conn.execute(text("SELECT name FROM test"))
  # g.conn.commit()

  # 2 ways to get results

  # Indexing result by column number
  # names = []
  # for result in cursor:
  #   names.append(result[0])  

  # Indexing result by column name
  # names = []
  # results = cursor.mappings.all()
  # for result in results:
  #   names.append(result["name"])
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  # return render_template("index.html", **context)
  return render_template('index.html')

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/interesting')
def interesting():
  return render_template("interesting.html")

# display all recipes in the database
@app.route('/recipes')
def recipes():
  print(request.args)
  
  cursor = g.conn.execute(text("SELECT recipe_name, instruction FROM rec_upload LIMIT 8"))
  g.conn.commit()

  #rec_names = []
  recipes_list = []
  for result in cursor:
    recipes_list.append({'name':result[0], 'instruction':result[1]})
  
  context = dict(data = recipes_list)

  return render_template("recipes.html", **context)

# add new recipe glbally
# to new recipe page
@app.route('/new_recipe')
def new_recipe():
  return render_template("new_recipe.html")

# add new recipe
@app.route('/add_recipe', methods=['POST'])
def add_recipe():
  msg = ''
  name = request.form['name']
  instruction = request.form['instruction']
  prep_time = request.form['prep_time']
  cook_time = request.form['cook_time']
  serving = request.form['serving']

  try:
    param_dict = {'name' : name, 'instruction' : instruction,
                  'prep_time' : prep_time, 'cook_time' : cook_time,
                  'serving' : serving}
    psql_query = 'INSERT INTO rec_upload (recipe_name, instruction, prep_time, cook_time, serving) VALUES(:name, :instruction, :prep_time, :cook_time, :serving)'
    g.conn.execute(text(psql_query), param_dict)
    g.conn.commit()
    msg = 'You\'ve just added a new recipe!'
    flash(msg)
  except Exception as e:
    print(f'Error: {e}')
    msg = 'Please fill in correct information'
    flash(msg)
    return redirect(url_for('new_recipe'))
  
  return render_template('success.html')

# Display recipes by categories
@app.route('/categories')
def show_categories():
  cursor = g.conn.execute(text("select * from categories"))
  category_list = []
  for category in cursor:
    category_list.append({'id':category[0], 'name':category[1]})
  return render_template('categories.html', categories=category_list)

@app.route('/category/<int:category_id>/recipes')
def category_recipes(category_id):
    # Fetch recipes for a given category
    recipes = g.conn.execute(text("select r.recipe_name, r.instruction, r.prep_time, r.cook_time, r.serving, r.recipe_id \
                                  from rec_upload r, characterize c \
                                  where c.recipe_id=r.recipe_id and c.cid = :cid"),{"cid": category_id}).fetchall()
    formatted_recipes = []
    for recipe in recipes:
      ingredients = g.conn.execute(text("select i.name,u.amount,i.unit \
                               from ingredients i, use u \
                               where i.name = u.name and u.recipe_id =:recipe_id"),{"recipe_id":recipe[5]}).fetchall()
      formatted_ingredients = "; ".join([f"{item[0].title()}: {item[1]} {item[2]}" for item in ingredients])
      formatted_recipes.append({"recipe_name": recipe[0], "instruction": recipe[1], "prep_time": recipe[2],"cook_time":recipe[3],"serving":recipe[4],"ingredients":formatted_ingredients})
    return render_template('show_recipes.html', recipes=formatted_recipes, category_id=category_id)

# ----- authentication system -----
# to login page
@app.route('/login_page')
def login_page():
  return render_template("login_page.html")

# login to account
@app.route('/login', methods=['GET','POST'])
def login():
  msg = ''
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    username = request.form['username']
    password = request.form['password']

    try:
      # check database
      psql_query = text('SELECT username, password, user_id FROM users WHERE username = :username')
      cursor = g.conn.execute(psql_query, {'username':username})
      account = cursor.fetchone()
      print(account)

    # check if such account exist
      if account and verify_password(account[1],password):
        session['loggedin'] = True
        session['username'] = account[0]
        session['user_id'] = account[2]
        return redirect(url_for('home'))
      else:
        msg = 'Incorrect username or passowrd.'

    except Exception as e:
      print(f'Error: {e}')
      msg = 'There is an error during login.'
  
  return render_template('login_page.html', msg=msg)

def verify_password(entry, record):
  return entry == record

# logout
@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  # Redirect to login page
  return redirect('/')


# ----- registration system ------
# to registration page
@app.route('/registration_page')
def registration_page():
  return render_template("registration_page.html")

@app.route('/register', methods=['GET','POST'])
def register():
  msg = ''
  username = request.form['username']
  password = request.form['password']
  user_profile = request.form['user_profile']
  param_dict = {'username' : username, 'password' : password, 'user_profile' : user_profile}
  
  try:
    psql_query = text('INSERT INTO users (username, password, user_profile) VALUES(:username, :password, :user_profile)')
    g.conn.execute(psql_query, param_dict)
    g.conn.commit()
    msg = 'Registration success'

  except Exception as e:
    print(f'Error: {e}')
    msg = 'There is an error during registration.'
    return render_template('registration_page.html', msg=msg)
  
  return render_template('login_page.html', msg=msg)


# user home page
@app.route('/login/home', methods=['GET'])
def home():
    # Check login status
    if 'loggedin' in session:
        # show homepage and profile
        user = session['username']
        profile_query = text('SELECT user_profile, user_id FROM users WHERE username = :username')
        param_dict = {'username': user}
        val = g.conn.execute(profile_query, param_dict).fetchone()

        # check membership status
        premium_query = text('SELECT payment_plan FROM premium_user WHERE user_id = :user_id')
        premium_val = g.conn.execute(premium_query, {'user_id': val[1]}).fetchone()
        membership_level = premium_val[0] if premium_val else None

        category_list = []
        categories = g.conn.execute(text("SELECT cid, cname FROM categories")).fetchall()
        for category in categories:
          category_list.append({'cid':category[0],"cname":category[1]})

        # fetch user recipes
        user_id = {'user_id':val[1]}
        cursor = g.conn.execute(text("SELECT recipe_name, instruction, recipe_id FROM rec_upload WHERE user_id =:user_id"), user_id)
        recipes_list = []
        for result in cursor:
          recipe_id = {"recipe_id":result[2]}
          # fetch ingredients 
          cursor2 = g.conn.execute(text("select i.name,u.amount,i.unit \
                               from ingredients i, use u \
                               where i.name = u.name and u.recipe_id =:recipe_id"),recipe_id)
          ingredients = cursor2.fetchall()
          formatted_ingredients = "; ".join([f"{item[0].title()}: {item[1]} {item[2]}" for item in ingredients])
          recipes_list.append({'name':result[0], 'instruction':result[1],'ingredients':formatted_ingredients})
          cursor2.close()
        context = dict(data = recipes_list, membership_level=membership_level,categories=category_list)   
        # g.conn.commit()
        g.conn.close()
        return render_template('home.html', username=session['username'], profile= val[0], **context)
    
    return redirect(url_for('login'))

# ----- logged-in user recipe -----
# user could add their recipe to the database
@app.route('/user_new_recipe', methods=['GET','POST'])
def user_new_recipe():
  # retrieve user inputs
  msg = ''
  name = request.form['name']
  instruction = request.form['instruction']
  prep_time = request.form['prep_time']
  cook_time = request.form['cook_time']
  serving = request.form['serving']

  # retrieve ingredients input
  ingredient_names = request.form.getlist('ingredient_name[]')
  amounts = request.form.getlist('amount[]')
  units = request.form.getlist('unit[]')  
  selected_category = request.form['category_id']
  # retrieve in-session user info
  try:
    user_id = session['user_id']
    param_dict = {'name' : name, 'instruction' : instruction,
                  'prep_time' : prep_time, 'cook_time' : cook_time,
                  'serving' : serving, 'user_id' : user_id} 
    psql_query = 'INSERT INTO rec_upload (recipe_name, instruction, prep_time, cook_time, \
                  serving, user_id) VALUES(:name, :instruction, :prep_time, :cook_time, :serving, :user_id) RETURNING recipe_id'
    recipe_id = g.conn.execute(text(psql_query), param_dict).fetchone()[0]
    # g.conn.execute(text(psql_query), param_dict)

    # insert into characterize 
    if selected_category and selected_category != 'None':
      g.conn.execute(text("INSERT INTO characterize (recipe_id, cid) VALUES (:recipe_id, :cid)"), {'recipe_id': recipe_id,'cid': selected_category})

    # insert ingredients info
    for name, amount, unit in zip(ingredient_names, amounts, units):
      # check whether the ingredient exists in ingredients or not
      existing_ingredient = g.conn.execute(text("SELECT * FROM ingredients WHERE name = :name"), {'name': name}).fetchone()
      if not existing_ingredient:
        # if not exist, insert into ingredients
        g.conn.execute(text("INSERT INTO ingredients (name, unit) VALUES (:name, :unit)"), {'name': name, 'unit': unit})
        # insert into use table
        g.conn.execute(text("INSERT INTO use (recipe_id, name, amount) VALUES (:recipe_id, :ingredient_name, :amount)"), {'recipe_id': recipe_id, 'ingredient_name': name, 'amount': amount})

    g.conn.commit()
    msg = 'New recipe added.'
    flash(msg)
    g.conn.close()
  except Exception as e:
    print(f'Error: {e}')
    msg = 'Please fill in correct information.'
    flash(msg)
    return redirect(url_for('home'))

  return redirect(url_for('home'))


# loggedin user can view full information of the recipes
@app.route('/loggedin_user_all_recipes', methods=['GET'])
def loggedin_user_all_recipes():
  cursor = g.conn.execute(text("SELECT r.recipe_id, r.recipe_name, u.username, r.on_date, r.instruction, \
                               r.prep_time, r.cook_time, r.serving\
                               FROM rec_upload r, users u WHERE r.user_id = u.user_id\
                               ORDER BY r.on_date DESC"))
  #g.conn.commit()
  info_list = []
  for result in cursor:
    info_list.append({'recipe_id':result[0], 'recipe_name':result[1], 'username':result[2], 'on_date':result[3],
                      'instruction':result[4], 'prep_time':result[5], 'cook_time':result[6], 'serving':result[7]})
  
  context = dict(data = info_list)
  cursor.close()
  return render_template("recipe_all_info.html", **context) 


# Save recipe feature at user_all_recipe page
@app.route('/save_recipe/<int:recipe_id>', methods=['GET','POST'])
def save_recipe(recipe_id):
  msg = ''
  user_id = session['user_id']

  # check if the user saved it or not, if not post request and save
  try:
    psql_query = text("SELECT EXISTS(\
                          SELECT 1 \
                          FROM saves s \
                          WHERE s.user_id = :user_id AND s.recipe_id = :recipe_id)")
    cursor = g.conn.execute(psql_query, {"user_id": user_id, "recipe_id": recipe_id})
    exists = cursor.scalar()
    if exists:
      msg = 'This recipe was already in your folder.'
      flash(msg)
    else:
      save_query = text("INSERT INTO saves (user_id, recipe_id) \
                         VALUES(:user_id, :recipe_id)")
      g.conn.execute(save_query, {"user_id":user_id, "recipe_id":recipe_id})
      g.conn.commit()
      msg = 'You successfully save the recipe.'
      flash(msg)
      g.conn.close()
  except Exception as e:
    print(f'Error: {e}')
    msg = 'An error occured.'
    flash(msg)
  
  return redirect(url_for('loggedin_user_all_recipes'))


# display recipes in saved folder
@app.route('/loggedin_user_saves', methods=['GET'])
def loggedin_user_saves():
  user_id = session['user_id']
  saves_query = text("SELECT r.recipe_id, r.recipe_name, s.on_date, \
                     r.instruction, r.prep_time, r.cook_time, r.serving \
                      FROM rec_upload r INNER JOIN saves s \
                          ON r.recipe_id = s.recipe_id \
                      WHERE s.user_id = :user_id \
                      ORDER BY s.on_date DESC")
  
  # select in session user id
  cursor = g.conn.execute(saves_query, {"user_id":user_id})
  info_list = []
  for result in cursor:
    info_list.append({'recipe_id':result[0], 'recipe_name':result[1], 'on_date':result[2],
                      'instruction':result[3], 'prep_time':result[4], 'cook_time':result[5], 'serving':result[6]})
    
  context = dict(data = info_list)
  return render_template("saves.html", username=session['username'], **context)


# delete saved recipes
@app.route('/delete_saved_recipe/<int:recipe_id>', methods=['GET','POST'])
def delete_saved_recipe(recipe_id):
  msg = ''
  user_id = session['user_id']

  try:
    psql_query = text("DELETE FROM saves\
                       WHERE user_id = :user_id AND recipe_id = :recipe_id")
    g.conn.execute(psql_query, {"user_id":user_id, "recipe_id":recipe_id}) 
    g.conn.commit()
    msg = 'You successfully delete it from your folder.'
    flash(msg)
  except Exception as e:
    print(f'Error: {e}')
    msg = 'An error occured.'
    flash(msg)
  
  return redirect(url_for('loggedin_user_saves'))



# Review feature
# Each recipe has its own review page that contains user reviews
# users can also add review under the review page
@app.route('/review_page/<int:recipe_id>', methods=['GET', 'POST'])
def review_page(recipe_id):
  msg = ''
  print('anything here')
  user_id = session['user_id']

  # check if the user review it or not
  
  review_query = text("SELECT u.username, r.text, r.likes, r.at_time\
                       FROM review r INNER JOIN users u \
                       ON r.user_id = u.user_id \
                       WHERE r.recipe_id = :recipe_id \
                       ORDER BY r.at_time DESC")
  cursor = g.conn.execute(review_query, {"recipe_id": recipe_id})
  review_list = []
  for result in cursor:
    review_list.append({'username': result[0], 'text':result[1], 'likes':result[2],
                        'at_time':result[3]})
  context = dict(data = review_list)
  cursor.close()
  return render_template("reviews.html", recipe_id=recipe_id, **context)
    # psql_query = text("SELECT EXISTS(\
    #                       SELECT 1 \
    #                       FROM review rw \
    #                       WHERE rw.user_id = :user_id AND rw.recipe_id = :recipe_id)")
    # cursor = g.conn.execute(psql_query, {"user_id":user_id, "recipe_id":recipe_id})
    # exists = cursor.scalar()

    # # if the user has reviewe the recipe, flash message
    # if exists:
    #   msg = "You have left a review before."
    #   flash(msg)
    # else:
    #   return 

# Add review
@app.route('/add_review/<int:recipe_id>', methods=['GET','POST'])
def add_review(recipe_id):
  msg = ''
  likes = ''
  user_id = session['user_id']
  content = request.form['content']
  url = f'/review_page/{recipe_id}'
  # print(request.form['like'])
  # print(type(request.form['like']))
  if request.form['like'] == "1":
    likes = "TRUE"
  else:
    likes = "FALSE"

  try:
    psql_query = text("SELECT EXISTS(\
                          SELECT 1 \
                          FROM review rw \
                          WHERE rw.user_id = :user_id AND rw.recipe_id = :recipe_id)")
    cursor = g.conn.execute(psql_query, {"user_id":user_id, "recipe_id":recipe_id})
    exists = cursor.scalar()
    if exists:
      msg = 'You have made a review before.'
      flash(msg)
    else:
      param_dict = {'user_id':user_id, 'recipe_id':recipe_id,'content':content, 'likes':likes}
      psql_query = text("INSERT INTO review (user_id, recipe_id, text, likes) \
                    VALUES(:user_id, :recipe_id, :content, :likes)")
      print(psql_query)
      g.conn.execute(psql_query, param_dict)
      g.conn.commit()
      msg = "Review added."
      flash(msg)
      g.conn.close()
  except Exception as e:
    print(f'Error: {e}')
    msg = 'Please fill in the review.'
    flash(msg)
    return redirect(url)
  
  return redirect(url)


# loggedin user announcement page
@app.route('/announcement', methods=['GET'])
def announcement():
  cursor = g.conn.execute(text("SELECT a.at_time, u.username, a.link, a.description\
                               FROM ann_post a, users u \
                               WHERE a.user_id = u.user_id \
                               ORDER BY a.at_time DESC \
                               LIMIT 10"))
  ann_list = []
  for result in cursor:
    ann_list.append({'time':result[0], 'user':result[1], 'link':result[2], 
                     'description':result[3]})
  
  context = dict(data=ann_list)

  return render_template("announcement_page.html", **context)

@app.route('/user_new_announcement', methods=['GET','POST'])
def user_new_announcement():
  msg = ''
  content = request.form['content']
  link = request.form['link']

  try:
    user_id = session['user_id']
    param_dict = {'link':link, 'content':content, 'user_id':user_id}
    query = text("INSERT INTO ann_post (link, description, user_id) \
                 VALUES(:link, :content, :user_id)")
    g.conn.execute(query, param_dict)
    g.conn.commit()
    msg = "New announcement posted"
    flash(msg)
    g.conn.close()
  except Exception as e:
    print(f'Error: {e}')
    msg = 'Please fill the form correctly'
    flash(msg)
    return redirect(url_for('announcement'))
  
  return redirect(url_for('announcement'))


# not used (test stuff)
# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   params_dict = {"name":name}
#   g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
#   g.conn.commit()
#   return redirect('/')


# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
