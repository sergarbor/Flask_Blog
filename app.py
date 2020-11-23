from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from access_lvl import  Access_lvl
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user

BLOGS_PER_PAGE = 5

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/sergio/Documents/projects/flask/blog.db'
app.config['SECRET_KEY'] = 'kc98qi3odc093rjc0w9u3lcfu8u4'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(90))
    access_lvl = db.Column(db.Integer)
    date_joined = db.Column(db.DateTime)


class MyModelView(ModelView):
    def is_accessible(self):
        return  current_user.is_authenticated and (current_user.access_lvl == str(Access_lvl.ADMIN.value))


admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Blogpost, db.session))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['username']).first()
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('index'))

        return '<h1>Invalid username or password</h1>'
        
    return render_template('login.html')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).paginate(page=page, per_page=BLOGS_PER_PAGE)
    return render_template('index.html', posts=posts)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/add')
@login_required
def add():
    return render_template('add.html')



@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug=True)