from flask import Flask, redirect, url_for,render_template, request, session
import json

app=Flask(__name__)

app.secret_key="ATM2"

def get_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
        return data

def update_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

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
        print("*****************",username, email, pin,"**********************")
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
    return render_template('forgotpin.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    return render_template('verify.html')

@app.route('/resetpin', methods=['GET', 'POST'])
def resetpin():
    return render_template('resetpin.html')

@app.route('/dashboard/<user>')
def dashboard(user):
    return f"Hello {user}, Welcome to the ATM"

@app.route('/checkBalance')
def checkBalance():
    return "Your balance is 2000/-"

if __name__ == '__main__':
    app.run(debug=True)