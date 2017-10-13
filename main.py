from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheeseface@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    blog_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.Text(65000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __init__(self,title,blog,user):
        self.title=title
        self.blog=blog
        self.user_id=user

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
       
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User {0}>'.format(self.email)

def invalid_email(address):
    if ("@" not in address) or ("." not in address):
        return True

    elif " " in address:
        return True

    elif (address.find("@")!=address.rfind("@")) or (address.find(".")!=address.rfind(".")) or (address.find("@")>address.find(".")):
        return True

    else:
        return False


@app.route('/logout')
def logout():
    del session['email']
    flash('You have logged out!')
    return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = user.email
            flash("Logged in")
            return redirect('/')
        else:
            flash("You either made a mistake in your login information, or you NEED to join our community.", 'error')
            return render_template('login.html',email=email)


    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        error = 0
        if invalid_email(email):
            flash('So... "' + email + '" is not a valid email address.','error')
            error = 1
        if password != verify:
            flash('Your Passwords do not Match', 'error')
            error = 1
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('There is already an account associated with {0}.'.format(email), 'error')
            error = 1
        if error == 1:
            return render_template('signup.html',email=email)
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/")
    else:
        return render_template('signup.html')











@app.route('/blog', methods=['POST', 'GET'])
def showblogs():
    blog_id=request.args.get('blog_id')
    if blog_id != None:
        blog_id=int(blog_id)
    blogs=Blog.query.order_by(Blog.blog_id.desc()).all()
    return render_template('blog.html',blogs=blogs,blog_id=blog_id)



@app.route('/newpost', methods=['POST', 'GET'])
def addpost():
    if 'email' not in session:
        return redirect('/login')

    title = 'Entry Title'
    entry = 'Share your thoughts'
    
    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['blogentry']
        error = 0
        if title == 'Entry Title':
            flash("Please Title Your Thoughts", 'error')
            error = 1
        if entry == 'Share your thoughts':
            flash("Please Enter Your Thoughts", 'error')
            error = 1
        if error == 1:
            return render_template('post.html',title=title,entry=entry)
        user = User.query.filter_by(email=session['email']).first()
        blog = Blog(title,entry,user)
        db.session.add(blog)
        db.session.commit()
        blog_id=Blog.query.order_by(Blog.blog_id.desc()).first().blog_id
        return redirect('/blog?blog_id={0}'.format(blog_id))


    return render_template('post.html',title=title,entry=entry)

@app.route('/', methods = ['POST', 'GET'])
def index():
    return redirect('/blog')




app.secret_key = 'Wyhguwd0UBwnEK0w'

if __name__ == "__main__":
    app.run()