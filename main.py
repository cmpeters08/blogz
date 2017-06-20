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
    body = db.Column(db.String(400))

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/newpost')
def index():
    return render_template('posts.html', pagetitle='', post_title='', body='', body_error='', title_error='')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
        pagetitle = "New Blog Entry"
        if request.method == 'POST':
            post_title = request.form['post-title']
            body = request.form['new-body']
            post_id = request.form['post-id']
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
                    
            new_entry = Blog(post_title, body)
            #creating new entry after checking validation
            db.session.add(new_entry)
            #this adds 'new_entry = Blog(post_title, body)' to my database. it has all of the information I need!
            db.session.commit()  

            #actually the final commit to add the entry to the database.
        #return render_template('posts.html', pagetitle=pagetitle, blog_post=blog_post, new_entry=new_entry)
        #return redirect('/blog')
        return redirect('/blog?id={0}'.format(new_entry.id))
        
@app.route('/blog', methods=['POST', 'GET'])
def main_page():
    some_key_word = request.args.get('id', None)
    title = request.args.get('post_title')
    body = request.args.get('body')
    if some_key_word is None:
        blog_post = Blog.query.all()
        return render_template('allposts.html', blog_post=blog_post)
    #I don't need to send parameters through redirect. all redirect does is push me to a new page. 
    #the database knows what we're tracking!
    if some_key_word:
        post_id = Blog.query.get(some_key_word)
        #the post_id query contains everthing I need for my post. id, body and title.
        #return redirect('/blog?id={}'.format(post_id))
    return render_template('singlepost.html', post_id=post_id)
    #return redirect('/blog?id={}'.format(post_id))




if __name__ == '__main__':
    app.run()