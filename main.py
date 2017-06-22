from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:jcEnnBaDcXc4Vl65@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) 
app.secret_key = 'y334dEsz&9ad'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(42))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/newpost')
def empty_post():
    return render_template('posts.html', pagetitle='', post_title='', body='', body_error='', title_error='')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
        pagetitle = "New Blog Entry"
        if request.method == 'POST':
            post_title = request.form['post-title']
            body = request.form['new-body']
            #request.form pulls the information from my form
            #new_entry calls the init in my class
            body_valid = True
            

            if len(body) is  0:
                body_valid = False
                body_error = 'Oops, it looks like you forgot to add a body!'
                return render_template('posts.html', pagetitle=pagetitle, body='', post_title=post_title, body_error=body_error)

            if len(post_title) is 0:
                title_valid = False
                title_error = 'Oops, it looks like you need a title for your post!'
                return render_template('posts.html', pagetitle=pagetitle, post_title='', body=body, body_error='',title_error=title_error)
            owner = User.query.filter_by(username=session['username']).first()
            new_entry = Blog(post_title, body, owner)
            db.session.add(new_entry)
            #this adds 'new_entry = Blog(post_title, body)' to my database. it has all of the information I need!
            db.session.commit()  
            #actually the final commit to add the entry to the database.
#TODO find a way to account for user id in the redirect. we need to handle that.
        return redirect('/blog?id={0}'.format(new_entry.id))

        
@app.route('/blog', methods=['POST', 'GET'])
def main_page():
    some_key_word = request.args.get('id', None)
    username = request.args.get('username', None)
    title = request.args.get('post_title')
    body = request.args.get('body')
    if username:
        user = User.query.filter_by(username=username).first()
        blog_post = Blog.query.filter_by(owner=user).all()
        #query string needs blogpost where username is username
        return render_template('user_page.html', blog_post=blog_post, username=username)
    if some_key_word is None:
        #if the browser passes through an id of None do this
        blog_post = Blog.query.all()
        return render_template('allposts.html', blog_post=blog_post)
    #I don't need to send parameters through redirect. all redirect does is push me to a new page. 
    #the database knows what we're tracking!
    if some_key_word:
        #if some_key_word is not none
        post_id = Blog.query.get(some_key_word)
        #the post_id query contains everthing I need for my post. id, body and title.
        return render_template('singlepost.html', post_id=post_id)
    
    


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            #this first checks if the user exists, if not it will not run
            #next it compares the password entered to the one in the database
            # "rememebr" that the user has logged in.
            #look up sessions , I think that's what we need here
            #if they successfully login
            session['username'] = username
            flash("You are logged in")
            #flash messages use the session to store the message for the next time the user comes back 
            return redirect('/newpost')
        else:
            #add a flash error message
            flash('Username or password is incorrect. or username does not exist', 'error')
            
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify-password']

        if len(username) < 3:
            flash("Username must be at least 3 characters long", "error")
            return render_template("signup.html")
        if len(password) < 3:
            flash("Password must be at least 3 characters long.", "error")
            return render_template("signup.html", username=username)
        if verify_password != password:
            flash("Passwords do not match please re-enter passwords", "error")
            return render_template("signup.html", username=username)

        #validate user's data, look at user signup for help
       
        #exisiting user looks at the database to see if that username already exists
        # video link http://education.launchcode.org/web-fundamentals/videos/get-it-done/login-register-handlers/
        #if the user does not already exist
        existing_user = User.query.filter_by(username=username).first()
        #existing user looks for the first instance of username in the class User table
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            #session uses cookies to track session
            return redirect('/newpost')
        else:
            #return flash error messages telling the user that the
            #username already exists
            flash("It looks like that user name already exists. Please enter a diffrent username")
            return render_template("signup.html", username=username)
            #keeping the username so user can modify it
    if request.method == 'GET':
        return render_template('signup.html')
    #return render_template('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'main_page']
    #routes we are allowed to access without logging in.
    if request.endpoint not in allowed_routes and 'username' not in session:
        #if the request is not in the allowed routes, and the user isn't logged in. go to login page.
        #the routes are the function names, not the route ('/url') names
        # 'username' not in session, says that 'username' is not currently logged in.
        flash("You have to be logged in to view that page", "error")
        return redirect('/login')



    
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    #blog_post = Blog.query.all()
    return render_template('index.html', users=users)
        

if __name__ == '__main__':
    app.run()