from flask import Flask, redirect, url_for,render_template, request

app=Flask(__name__)

user="Ajay"

@app.route('/')
def base():
    return redirect("login")
    # can also use url_for which will call the logins function, redirect calls the router

@app.route("/login", methods=['GET', "POST"])
def logins():
    if request.method=='POST':
        mail=request.form.get('email')
        password=request.form.get('password')
        print("*****************",mail, password,"**********************")
        username=mail.split('@')[0]
        return redirect(url_for('dashboard',user=username))
    return render_template('login.html')

@app.route("/register")
def register():
    return 'Register'

@app.route('/dashboard/<user>')
def dashboard(user):
    return f"Hello {user}, Welcome to the ATM"

@app.route('/checkBalance')
def checkBalance():
    return "Your balance is 2000/-"

if __name__ == '__main__':
    app.run(debug=True)