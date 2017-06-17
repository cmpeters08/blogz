from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablog:buildit@localhost:8889/buildablog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)  

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))


@app.route('/', methods=['POST', 'GET'])
def index():
        if request.method == 'POST':
            post_title = request.form['post-title']
            body = request.form['new-body']
            db.session.add(post_title)
            db.session.add(body)
            db.session.commit()
            
        blog_post = Blog.query.all()
        return render_template('posts.html', pagetitle="My Blog", blog_post=blog_post )




app.run()