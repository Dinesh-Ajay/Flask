from flask import Flask, render_template, request, redirect, url_for, session
import random
import bcrypt
from database import db

app = Flask(__name__)


@app.route("/")
def home():
    return redirect(url_for("login"))



@app.route('/login',methods = ['GET','POST'])
def login():
    info=request.args.get('info')
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        cursor=db.cursor()
        cursor.execute("SELECT id,username,password FROM users WHERE email=%s",(email,))
        user=cursor.fetchone()

        password_check=bcrypt.checkpw(password.encode('utf-8'),user[2].encode('utf-8'))


        if user and password_check:
            session['uname']=user[1]
            session['user_id']=user[0]
            return redirect(url_for('dashboard'))
        return redirect(url_for("login",info="Invalid login"))


    return render_template("login.html",info=info)
    





@app.route("/register",methods=["GET","POST"])
def register():
    info=request.args.get("info")
    if request.method=="POST":
        username=request.form.get("uname")
        email=request.form.get("email")
        password=request.form.get("password")
        hashed_password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')

        cursor=db.cursor()
        cursor.execute("Select email FROM users WHERE email=%s",(email,))
        user=cursor.fetchone()
        if user:
            return redirect(url_for('register',info="Email is already registered"))
        cursor.execute("INSERT INTO users(username,email,password) VALUES (%s,%s,%s)", (username,email,hashed_password))
        db.commit()
        return redirect(url_for('login',info="Registration Successfull"))

    return render_template("register.html",info=info)




@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")




@app.route("/verify")
def verify():
    return render_template("verify.html")



@app.route("/resetpassword")
def resetpassword():
    return render_template("resetpassword")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        user_id=session['user_id']
        cursor=db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes WHERE user_id=%s ORDER BY created_at DESC",(user_id,))
        notes=cursor.fetchall()
        cursor.close()
        return render_template("dashboard.html",notes=notes)
    return redirect(url_for('login'))

@app.route('/editnote/<int:note_id>',methods=['GET','POST'])
def edit_note(note_id):
    if 'user_id' in session:
        cursor=db.cursor(dictionary=True)
        if request.method=='POST':
            new_content=request.form.get('content')
            cursor.execute("UPDATE notes SET content=%s WHERE id=%s AND user_id=%s",(new_content,note_id,session['user_id']))
            db.commit()
            return redirect(url_for('dashboard'))
        cursor.execute("SELECT * FROM notes WHERE id=%s AND user_id=%s",(note_id,session['user_id']))
        note=cursor.fetchone()
        cursor.close()
        if note:
            return render_template('editnote.html',note=note)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
