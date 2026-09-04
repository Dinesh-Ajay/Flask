from flask import Flask, redirect, url_for,render_template, request, session
import json
from mail import send_email
import random
import os

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
    info = request.args.get('info')
    if request.method=='POST':
        mail=request.form.get('email')
        pin=request.form.get('pin')
        data=get_data()
        users = data['users']
        for i in users:
            if i['email'] == mail and i['pin'] == pin:
                session['username'] = i['username']
                session['id']=i['id']
                return redirect(url_for('dashboard',user=session['username']))
        return redirect(url_for('login.html', info="Invalid login"))
    return render_template('login.html', info=info)

@app.route("/register", methods=['GET', "POST"])
def register():
    info = request.args.get('info')
    if request.method=='POST':
        username=request.form.get('uname')
        email=request.form.get('email')
        pin=request.form.get('pin')
        data=get_data()
        users = data["users"]
        for i in users:
            if i["email"] == email:
                return redirect(url_for('register.html', info="Email is already registered"))
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
    return render_template('register.html', info=info)

@app.route('/forgotpin', methods=['GET', 'POST'])
def forgotpin():
    info = request.args.get('info')
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
                return redirect(url_for('verify'))
        return redirect(url_for('forgotpin.html', info='Invalid Email or Email is not registered'))
    return render_template('forgotpin.html',info=info)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    info = request.args.get('info')
    if request.method=='POST':
        otp = request.form.get('otp')
        if session['otp']==otp:
            session['otp']=None
            return redirect(url_for('resetpin'))
        return redirect(url_for('verify.html', info="Invalid OTP")) 
    return render_template('verify.html',info=info)

@app.route('/resetpin', methods=['GET', 'POST'])
def resetpin():
    info = request.args.get('info')
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
                        return redirect(url_for('logins'))
        return redirect(url_for('resetpin.html', info='Enter the password correctly'))
    return render_template('resetpin.html',info=info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('logins')

@app.route('/dashboard/<user>')
def dashboard(user):
    if session.get('id'):
        return render_template('dashboard.html')
    return redirect(url_for('logins'))

@app.route('/checkBalance')
def checkBalance():
    if session.get('id'):
        data=get_data()
        users = data["users"]
        for i in users:
            if i['id']==session['id']:
                balance=i['balance']
                return render_template('checkBalance.html', user=session["username"],balance=balance)        
    return redirect(url_for('logins'))    

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    if session.get('id'):
        info = request.args.get('info')
        if request.method=='POST':
            try:
                amount = int(request.form.get('amount'))
            except Exception:
                return render_template("deposit.html",
                                    username = session['username'],
                                    info="Enter the proper amount")
            data = get_data()
            users = data["users"]
            for i in users:
                if i["id"] == session["id"]:
                    i["balance"]+=amount
                    i["history"].append(f"{amount} deposited")
                    update_data(data)
                    return redirect('checkBalance')
        return render_template("deposit.html",info=info)        
    return redirect(url_for('logins'))    

@app.route('/withdraw',methods=['POST','GET'])
def withdraw():
    if session.get('id'):
        info = request.args.get('info')
        if request.method=='POST':
            try:
                amount = int(request.form.get('amount'))
                if amount < 0:
                    raise Exception("Enter the proper amount")
            except Exception:
                return redirect(url_for("withdraw.html",
                                    username = session['username'],
                                    info="Enter the proper amount"))
            data = get_data()
            users = data["users"]
            for i in users:
                if i["id"] == session["id"]:
                    if i["balance"]>=amount:
                        i["balance"]-=amount
                        i["history"].append(f"{amount} Withdraw")
                        update_data(data)
                        return redirect(url_for('checkBalance'))
                    return redirect(url_for("withdraw.html",
                                    username = session['username'],
                                    info="Insufficent balance"))
        return render_template('withdraw.html',info=info)        
    return redirect(url_for('logins'))    

@app.route('/viewtransactions')
def viewtransactions():
    if session.get('id'):
        data = get_data()
        users = data["users"]
        for i in users:
            if i["id"]==session["id"]:
                history = i["history"]
                lenght = len(history)
                return render_template("viewtransactions.html",
                                    history=history,
                                    lenght=lenght)        
    return redirect(url_for('logins'))

if __name__ == '__main__':
    app.run(debug=True)