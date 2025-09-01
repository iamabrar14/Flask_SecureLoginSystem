from flask import Flask,render_template,request,redirect,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
#Configuring Database
app.secret_key="your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

#Database Model+Password hashing

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(25),nullable=False,unique=True)
    password_hash=db.Column(db.String(150),nullable=False)
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

#routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html")

#Login Route
@app.route("/login",methods=["POST"])
def login():
    #Collect info from form and check info from database
    username=request.form["username"]
    password=request.form["password"]
    user=User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["username"]=username
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html", error="Invalid username or password")

#Register Route
@app.route("/register", methods=["POST"])
def register():
    username=request.form["username"]
    password=request.form["password"]
    user=User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="User is already registered")
    else:
        new_user=User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username']=username
        return redirect(url_for('dashboard'))

#Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html",username=session['username'])
    return redirect(url_for('home'))

#Logout
@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))
    
if __name__=="__main__":
    with app.app_context(): #Creating database
        db.create_all()
    app.run(debug=True)