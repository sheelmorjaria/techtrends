import sqlite3
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime
import sys
connection_count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global connection_count
    connection = get_db_connection()
    connection_count += 1
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global connection_count
    connection = get_db_connection()
    connection_count += 1
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " " + "Article with id: %s does not exist!", post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " " + "Article %s retrieved!", post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " " + 'About page retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            global connection_count
            connection = get_db_connection()
            connection_count += 1
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            #log event
            app.logger.info(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " " + 'Article "%s" created!', title)
            #log_events('Article "%s" created!', title) 
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

#Total amount of posts in the database
#Total amount of connections to the database. 
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response = app.response_class(
        response=json.dumps({"db_connection_count":connection_count,"post_count":len(posts)}),
        status=200,
        mimetype='application/json'
    )
    return response


#log events, article title,non-existing article accessed, about us retrieved, when new article is created, to stdout


# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
