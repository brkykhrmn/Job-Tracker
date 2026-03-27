from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = "secretkey"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Job %r>' %self.id
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)


class SignUp(FlaskForm):
    username = StringField(validators = [InputRequired(), length(min = 4, max = 20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(), length(min = 4, max = 20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user_check = User.query.filter_by(username=username.data).first()

        if user_check:
            raise ValidationError("Nah")

class LogIn(FlaskForm):
    username = StringField(validators = [InputRequired(), length(min = 4, max = 20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(), length(min = 4, max = 20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Log In")


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        company = request.form["Company"]
        position = request.form["Position"]
        status = request.form["Status"]

        new_application = Job(company=company, position=position, status=status)

        try:
            db.session.add(new_application)
            db.session.commit()
            return redirect('/')
        
        except:
            return 'Error'

    else:
        application = Job.query.order_by(Job.date_created).all()
        return render_template("index.html", application=application)
    

@app.route("/delete/<int:id>")
def delete(id):
    application_to_delete = Job.query.get_or_404(id)

    try:
        db.session.delete(application_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return 'Error'
    

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    application_to_update = Job.query.get_or_404(id)

    if request.method == 'POST':
        application_to_update.company = request.form['Company']
        application_to_update.position = request.form['Position']
        application_to_update.status = request.form['Status']

        try:
            db.session.commit()
            return redirect('/')
        
        except:
            return 'Error'

    else:
        return render_template("update.html", application_to_update=application_to_update)


@app.route("/log_in")
def log_in():
    form = LogIn()

    

    return render_template("/log_in.html", form=form)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUp()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)

        new_user = User(username = form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('log_in'))
    
    return render_template("/sign_up.html", form=form)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=3000, debug=True)