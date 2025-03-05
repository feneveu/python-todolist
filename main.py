from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


# Configure the Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'


# Initialize database
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to login page if not authenticated


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(100), unique=True, nullable=False)
    password = db.Column(String(500), nullable=False)
    task = relationship('Task', back_populates="user")


# Tasks Table
class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    importance = db.Column(Integer, nullable=False)
    due_date = db.Column(String(10), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Link tasks to users
    user = relationship("User", back_populates="task")


# create all database elements/tables
with app.app_context():
    db.create_all()


# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
@login_required  # Ensures only logged-in users can access
def index():
    """home page of each individual user"""

    # whether the page is sorted by importance or date
    sort_by = request.args.get('sort_by', 'importance')

    # if by date, order by ascending
    if sort_by == 'date':
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc()).all()
    # if by importance, order by desc
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.importance.desc()).all()

    # return the index template with all the needed info
    return render_template('index.html', tasks=tasks, sort_by=sort_by, user=current_user)


@app.route('/add_task', methods=['GET', 'POST'])
@login_required  # must be a user to access
def add_task():
    """adds a task to the users task list"""

    if request.method == 'POST':
        # get the task from the entry
        task_name = request.form.get('task')
        # get the impotance from the slider
        importance = int(request.form.get('importance'))
        # either the due date exists or not
        due_date = request.form.get('due_date') or "No Date"

        # Create a new task and add it to the database
        new_task = Task(name=task_name, importance=importance, due_date=due_date, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

        flash("Task added successfully!", "success")  # Flash success message to board
        return redirect(url_for('index'))  # Redirect to index after adding task

    return render_template('add_task.html')


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required  # needs to be a user to access
def edit_task(task_id):
    """edits a given task"""

    # find the task if it exists
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        # collect the data from user
        task.name = request.form.get('task')
        task.importance = int(request.form.get('importance'))
        due_date = request.form.get('due_date')
        # id of user is the current_user.id
        task.user_id = current_user.id

        task.due_date = due_date if due_date else "No Date"

        # commit changes to the database
        db.session.commit()
        # return to the front page
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)


@app.route('/delete_task/<int:task_id>')
@login_required  # needs to be a user to access
def delete_task(task_id):
    """deletes a given task"""

    task = Task.query.get_or_404(task_id)
    # commit delete to the database
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """login, doesn't have to be user"""

    # checks if the user entered information
    if request.method == 'POST':
        # saves the given email and password
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        # check if the user exists and check if the password matches the hashed password for said user
        if user and check_password_hash(user.password, password):
            login_user(user)  # This logs the user in
            return redirect(url_for('index'))
        else:
            # will show to screen invalid error
            flash("Invalid credentials. Please try again.", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """logs the current user out"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """signs up new user"""

    # checks if user has given any information
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # check if the passwords entered match
        if password != confirm_password:
            flash("Passwords don't match", "danger")
            return redirect(url_for('signup'))

        # check to see if this user is an existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for('login'))

        # if all passes, then hash the given password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # create a new user in the database
        new_user = User(email=email, password=hashed_password)
        # commit to the table
        db.session.add(new_user)
        db.session.commit()

        # give the green light to the user
        flash("Account created! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
