from flask import Flask, render_template, redirect, session, flash, request
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"


app.app_context().push()
connect_db(app)

db.create_all()

@app.route("/")
def home():
    return redirect('/register')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username,password,first_name,last_name,email)
        session["user_id"] = user.user_id
        db.session.add(user)
        db.session.commit()
        return redirect(f"/users/{user.username}")

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
    else:
        return render_template('login_form.html', form=form)
    
@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/")


@app.route("/users/<username>", methods=["GET", "POST"])
def show_user_page(username):

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")
    user = User.query.filter_by(username=username).one()
    feedback = Feedback.query.filter_by(username=username)
    # if i were going to do a page with details of the feedback that was clicked on
    # i would need a new route to display the feed back and I would use this feedback line
    return render_template("details.html", user=user, feedback=feedback)

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):

    if "username" not in session or username!= session['username']:
        raise Unauthorized()

    # if request.method == "POST":
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)  
        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{username}")
    
    else:
          
        return render_template("add_feedback.html", form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")


@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback(id):
    username = session.get('username')
    
    if "username" not in session or username!= session['username']:
        raise Unauthorized()
    
    user = User.query.filter_by(username=username).first()
    feedback = Feedback.query.filter_by(id=id).first()  
    
    if not feedback:
        return "Feedback not found.", 
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("edit_feedback.html", user=user, form=form, feedback=feedback,)


    
    


