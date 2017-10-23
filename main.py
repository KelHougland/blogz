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
    user = db.relationship('User')

    def __init__(self,title,blog,user):
        self.title=title
        self.blog=blog
        self.user_id=user

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    # blogs = db.relationship('Blog',backref='user_id')
       
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return '<User {0}>'.format(self.user_name)

def invalid_user_name(user_name):
    if len(user_name)<3:
        return True

    elif " " in user_name:
        return True

    else:
        return False


@app.route('/logout')
def logout():
    del session['user_name']
    flash('You have logged out!')
    return redirect('/blog')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        user = User.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            session['user_name'] = user.user_name
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash("You either made a mistake in your login information, or you NEED to join our community.", 'error')
            return render_template('login.html',user_name=user_name)


    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        verify = request.form['verify']
        error = 0
        if invalid_user_name(user_name):
            flash('So... "' + user_name + '" is not a valid user_name address.','error')
            error = 1
        if password != verify:
            flash('Your Passwords do not Match', 'error')
            error = 1
        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            flash('There is already an account associated with {0}.'.format(user_name), 'error')
            error = 1
        if error == 1:
            return render_template('signup.html',user_name=user_name)
        user = User(user_name=user_name, password=password)
        db.session.add(user)
        db.session.commit()
        session['user_name'] = user.user_name
        return redirect("/")
    else:
        return render_template('signup.html')




@app.route('/blog', methods=['POST', 'GET'])
def showblogs():
    blog_id=request.args.get('blog_id')
    user_id=request.args.get('user_id')
    if blog_id != None:
        blog_id=int(blog_id)
    if user_id != None:
        blogs = Blog.query.filter_by(user_id=user_id).order_by(Blog.blog_id.desc()).all()
        user_name = User.query.filter_by(user_id=user_id).first().user_name
        return render_template('singleUser.html',blogs=blogs,user_name=user_name)
    blogs=Blog.query.order_by(Blog.blog_id.desc()).all()
    return render_template('blog.html',blogs=blogs,blog_id=blog_id,user_id=user_id)



@app.route('/newpost', methods=['POST', 'GET'])
def addpost():
    if 'user_name' not in session:
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
        user = User.query.filter_by(user_name=session['user_name']).first().user_id
        blog = Blog(title,entry,user)
        db.session.add(blog)
        db.session.commit()
        blog_id=Blog.query.order_by(Blog.blog_id.desc()).first().blog_id
        return redirect('/blog?blog_id={0}'.format(blog_id))


    return render_template('post.html',title=title,entry=entry)

@app.route('/', methods = ['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',users=users)


@app.before_request
def require_login():
    allowed_routes = ['login','signup','showblogs','index']
    if (request.endpoint not in allowed_routes) and ('user_name' not in session):
        return redirect('/login')


app.secret_key = 'Wyhguwd0UBwnEK0w'

if __name__ == "__main__":
    app.run()