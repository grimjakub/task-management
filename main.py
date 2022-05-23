from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


##CREATE TABLE
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'


## crate database if not exit
# if not os.path.isfile('sqlite:///tasks.db'):
# db.create_all()


@app.route('/')
def home():
    all_tasks = db.session.query(Task).all()
    return render_template("index.html", tasks=all_tasks)


@app.route('/filter', methods=["GET", "POST"])
def filter_task():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    if request.method == "POST":
        searching_word = request.form["filter"]
        if searching_word == "":
            return redirect(url_for("home"))
        filter_tasks = db.session.query(Task).filter(Task.title.like(searching_word))
        return render_template("index2.html", tasks=filter_tasks)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        if request.form["title"] == "":
            return redirect(url_for("home"))
        new_task = Task(
            title=request.form["title"],
            description=request.form["description"],
            status="todo",
            deadline=request.form["deadline"]
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")


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
    return render_template("detail.html", task=task_selected)


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
    if request.method == "POST":
        # UPDATE RECORD
        task_id = request.form["id"]
        task_to_update = Task.query.get(task_id)
        task_to_update.title = request.form["title"]
        task_to_update.description = request.form["description"]
        db.session.commit()
        return redirect(url_for('home'))
    task_id = request.args.get('id')
    task_selected = Task.query.get(task_id)
    return render_template("edit.html", task=task_selected)


if __name__ == "__main__":
    app.run(debug=True)
