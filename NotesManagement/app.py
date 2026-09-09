from flask import Flask, redirect, url_for,render_template, request, session
import json
from mail import send_email
import random

app=Flask(__name__)

app.secret_key="ATM2"

def get_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
        return data

def update_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def generate_otp():
    return str(random.randint(100000, 999999))

user="Ajay"

@app.route('/')
def base():
    return redirect("login")
    # can also use url_for which will call the logins function, redirect calls the router

@app.route("/login", methods=['GET', "POST"])
def logins():
    if request.method=='POST':
        mail=request.form.get('email')
        pin=request.form.get('pin')
        data=get_data()
        users = data['users']
        for i in users:
            if i['email'] == mail and i['pin'] == pin:
                session['username'] = i['username']
                return redirect(url_for('dashboard',user=session["username"]))
        else:
            return render_template('login.html', info="Invalid login")
    return render_template('login.html')

@app.route("/register", methods=['GET', "POST"])
def register():
    if request.method=='POST':
        username=request.form.get('uname')
        email=request.form.get('email')
        pin=request.form.get('pin')
        data=get_data()
        users = data["users"]
        for i in users:
            if i["email"] == email:
                return render_template('register.html', info="Email is already registered")
        
        details = {
            "id": len(users)+1,
            "username":username,
            "email":email,
            "pin":pin,
            "history":[],
            "balance":0
        }
        users.append(details)
        update_data(data)
        return redirect('login')

    return render_template('register.html')

@app.route('/forgotpin', methods=['GET', 'POST'])
def forgotpin():
    if request.method=='POST':
        email = request.form.get('email')
        data=get_data()
        users = data["users"]
        for i in users:
            if email == i['email']:
                username=i['username']
                otp=generate_otp() 
                send_email(email, username, otp)
                session['otp']=otp
                session['email']=email
                return redirect('verify')

        return render_template('forgotpin.html', info='Invalid email')

    return render_template('forgotpin.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method=='POST':
        otp = request.form.get('otp')
        if session['otp']==otp:
            session['otp']=None
            return redirect('resetpin')
        
        return render_template('verify.html', info="Invalid OTP")

    return render_template('verify.html')

@app.route('/resetpin', methods=['GET', 'POST'])
def resetpin():
    if request.method=='POST':
        npin = request.form.get('npin')
        cpin = request.form.get('cpin')
        if npin==cpin:
                data=get_data()
                users = data["users"]
                for i in users:
                    if i['email']==session['email']:
                        i['pin']=npin
                        update_data(data)
                        return redirect('login')
                    
        return render_template('resetpin.html', info='Enter the password correctly')

    return render_template('resetpin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('login')

@app.route('/dashboard/<user>')
def dashboard(user):
    return f"Hello {user}, Welcome to the ATM"

@app.route('/checkBalance')
def checkBalance():
    return "Your balance is 2000/-"

if __name__ == '__main__':
    app.run(debug=True)
