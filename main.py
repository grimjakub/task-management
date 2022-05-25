from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sdsd684f3s687ed445FDFASDF'
app.config['UPLOAD_FOLDER'] = 'upload/'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # tasks = relationship("Task", back_populates="user")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # user = relationship("User", back_populates="tasks")
    title = db.Column(db.String(500), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.String(30), nullable=False)
    file_path = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'


# db.create_all()


@app.route('/')
def home():
    if current_user.is_active == False:
        return render_template("authentication.html",
                               current_user=current_user)
    all_tasks = db.session.query(Task).filter(
        Task.user_id.like(current_user.id))
    return render_template("index.html", tasks=all_tasks,
                           current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            new_user = User(
                username=request.form["username"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"],
                                                method="pbkdf2:sha256",
                                                salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        except:
            return render_template("register.html", current_user=current_user)
    return render_template("register.html", current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/show_finished', methods=["GET", "POST"])
def show_finished():
    all_tasks = db.session.query(Task).all()
    finished_tasks = [task for task in all_tasks if task.status == "✓"]
    return render_template("index.html", tasks=finished_tasks,
                           current_user=current_user)


@app.route('/show_todo', methods=["GET", "POST"])
def show_todo():
    all_tasks = db.session.query(Task).all()
    todo_tasks = [task for task in all_tasks if task.status == "todo"]
    return render_template("index.html", tasks=todo_tasks,
                           current_user=current_user)


@app.route('/', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        searching_word = request.form["search"]
        filter_tasks = db.session.query(Task).filter(
            Task.title.like(f"%{searching_word}%"))
        return render_template("index.html", tasks=filter_tasks,
                               current_user=current_user)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        if request.form["title"] == "":
            return redirect(url_for("home"))

        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(
                os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            filepath = ""
        new_task = Task(
            title=request.form["title"],
            description=request.form["description"],
            status="todo",
            deadline=request.form["deadline"],
            user_id=current_user.id,
            file_path=filepath
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("add.html", current_user=current_user)


@app.route('/download', methods=["GET"])
def download_file():
    path = request.args.get('file')
    return send_file(path, as_attachment=True)


@app.route("/delete")
def delete():
    task_id = request.args.get("id")
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/detail", methods=["GET"])
def detail():
    task_id = request.args.get('id')
    task_selected = Task.query.get(task_id)
    return render_template("detail.html", task=task_selected,
                           current_user=current_user)


@app.route("/status")
def status():
    task_id = request.args.get('id')
    task_to_update = Task.query.get(task_id)
    if task_to_update.status == "todo":
        task_to_update.status = "✓"
    elif task_to_update.status == "✓":
        task_to_update.status = "todo"
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    task_id = request.args.get('id')
    task_selected = Task.query.get(task_id)
    if request.method == "POST":
        task_to_update = task_selected
        task_to_update.title = request.form["title"]
        task_to_update.description = request.form["description"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", task=task_selected,
                           current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
