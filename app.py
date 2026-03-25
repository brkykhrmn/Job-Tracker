from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Job %r>' %self.id

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)