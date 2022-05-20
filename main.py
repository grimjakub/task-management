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
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'


## crate database if not exit
# if not os.path.isfile('sqlite:///tasks.db'):
#     db.create_all()


@app.route('/')
def home():
    all_tasks = db.session.query(Task).all()
    return render_template("index.html", tasks=all_tasks)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_task = Task(
            title=request.form["title"],
            description=request.form["description"],
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


if __name__ == "__main__":
    app.run(debug=True)
