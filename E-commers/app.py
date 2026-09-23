from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import re

from database import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from mail import send_email


app = Flask(__name__)
app.secret_key = "my-secret-key"
s = URLSafeTimedSerializer(app.secret_key)




@app.route("/")
def home():
    return redirect(url_for("login"))



@app.route("/login", methods=["GET", "POST"])
def login():
    info = request.args.get("info")
    if request.method == "POST":
        login_input = request.form.get("login_input", "").strip()
        password = request.form.get("password", "")
        if not login_input or not password:
            return redirect(url_for("login",info="Email/Phone and password are required."))
        cursor = db.cursor()
        cursor.execute(""" SELECT id, name, email, password, two_step_verification FROM users WHERE email = %s OR phone = %s""",(login_input, login_input))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            return redirect(url_for("login",info="Invalid email/phone or password."))
        user_id = user[0]
        name = user[1]
        email = user[2]
        stored_password = user[3]
        two_step_verification = user[4]
        password_check = bcrypt.checkpw(password.encode("utf-8"),stored_password.encode("utf-8"))
        if not password_check:
            return redirect(url_for("login",info="Invalid email/phone or password."))
        if two_step_verification:
            import random
            from datetime import datetime, timedelta
            otp = str(random.randint(100000, 999999))
            session["pending_user_id"] = user_id
            session["pending_user_name"] = name
            session["pending_user_email"] = email
            session["login_otp"] = otp
            session["otp_expiry"] = (datetime.now() + timedelta(minutes=5)).timestamp()
            subject = "ShopSphere - Login Verification Code"
            body = f"""Hello {name},Your ShopSphere login verification code is:{otp}
            This OTP will expire in 5 minutes.
            If you did not try to login to your ShopSphere account,
            please ignore this email.
            Regards,
            ShopSphere Team
            """
            email_sent = send_email(email,subject,body)
            if email_sent:
                return redirect(url_for("verify"))
            session.pop("pending_user_id", None)
            session.pop("pending_user_name", None)
            session.pop("pending_user_email", None)
            session.pop("login_otp", None)
            session.pop("otp_expiry", None)
            return redirect(url_for("login",info="Unable to send verification code. Please try again."))
        session["user_id"] = user_id
        session["uname"] = name
        return redirect(url_for("dashboard"))
    return render_template("login.html",info=info)


@app.route("/register", methods=["GET", "POST"])
def register():
    info = request.args.get("info")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not name or not email or not phone or not password or not confirm_password:
            return redirect(url_for("register", info="All fields are required."))
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_pattern, email):
            return redirect(url_for("register", info="Please enter a valid email address."))
        phone_pattern = r"^[6-9][0-9]{9}$"
        if not re.match(phone_pattern, phone):
            return redirect(url_for("register",info="Please enter a valid 10-digit phone number."))
        password_pattern = (r"^(?=.*[a-z])" r"(?=.*[A-Z])" r"(?=.*\d)" r"(?=.*[@$!%*?&])" r".{8,}$")
        if not re.match(password_pattern, password):
            return redirect(url_for("register",info=("Password must contain at least 8 characters, " "one uppercase letter, one lowercase letter, " "one number and one special character.")))
        if password != confirm_password:
            return redirect(url_for("register", info="Passwords do not match."))
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s",(email,))
        existing_email = cursor.fetchone()
        if existing_email:
            cursor.close()
            return redirect(url_for("register", info="Email is already registered."))
        cursor.execute("SELECT id FROM users WHERE phone=%s",(phone,))
        existing_phone = cursor.fetchone()
        if existing_phone:
            cursor.close()
            return redirect(url_for("register", info="Phone number is already registered."))
        hashed_password = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")
        two_step_verification = 1 if request.form.get("two_step_verification") else 0
        cursor.execute(""" INSERT INTO users (name, email, phone, password, two_step_verification) VALUES (%s, %s, %s, %s, %s) """,
            (name,email,phone,hashed_password,two_step_verification))
        db.commit()
        cursor.close()
        return redirect(url_for("login",info="Registration successful. Please login."))
    return render_template("register.html",info=info)




@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "pending_user_id" not in session:
        return redirect(url_for("login",info="Please login first."))
    info = request.args.get("info")
    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        stored_otp = session.get("login_otp")
        otp_expiry = session.get("otp_expiry")
        if not stored_otp or not otp_expiry:
            return redirect(url_for("login",info="OTP session expired. Please login again."))
        from datetime import datetime
        if datetime.now().timestamp() > otp_expiry:
            session.pop("pending_user_id", None)
            session.pop("pending_user_name", None)
            session.pop("pending_user_email", None)
            session.pop("login_otp", None)
            session.pop("otp_expiry", None)
            return redirect(url_for("login",info="OTP expired. Please login again."))
        if entered_otp != stored_otp:
            return redirect(url_for("verify",info="Invalid OTP. Please try again."))
        session["user_id"] = session["pending_user_id"]
        session["uname"] = session["pending_user_name"]
        session.pop("pending_user_id", None)
        session.pop("pending_user_name", None)
        session.pop("pending_user_email", None)
        session.pop("login_otp", None)
        session.pop("otp_expiry", None)
        return redirect(url_for("dashboard"))
    return render_template("verify.html",info=info)




@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login", info="Please login first."))
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            id,
            name,
            category,
            description,
            price,
            stock,
            image,
            rating
        FROM products
        WHERE stock > 0
        ORDER BY id DESC
    """)
    products = cursor.fetchall()
    cursor.close()
    return render_template(
        "dashboard.html",
        products=products,
        name=session.get("uname")
    )



@app.route('/productdetails/<int:product_id>')
def productdetails(product_id):
    cursor=db.cursor(dictionary=True)
    cursor.execute(""" SELECT id,name,category,description,price,stock,image,rating FROM products WHERE id = %s """,(product_id,))
    product=cursor.fetchone()
    cursor.close()
    return render_template('productdetails.html',product=product)




@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    info = request.args.get("info")
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return redirect(url_for("forgotpassword",info="Please enter your email address."))
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_pattern, email):
            return redirect(url_for("forgotpassword",info="Please enter a valid email address."))
        cursor = db.cursor()
        cursor.execute(""" SELECT name FROM users WHERE email = %s """, (email,))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            return redirect(url_for("forgotpassword",info="Email is not registered."))
        name = user[0]
        token = s.dumps(email,salt="password-reset-salt")
        reset_url = url_for("resetpassword",token=token,_external=True)
        subject = "ShopSphere - Password Reset"
        body = f""" Hello {name}, We received a request to reset your ShopSphere password.Click the link below to reset your password: {reset_url}
                            This link will expire in 10 minutes.
                            If you did not request a password reset,
                            please ignore this email.
                            Regards,
                            ShopSphere Team """
        email_sent = send_email(email,subject,body)
        if email_sent:
            return redirect(url_for("forgotpassword",info="Reset link sent to your email. Please check your inbox."))
        return redirect(url_for("forgotpassword", info="Unable to send reset email. Please try again."))
    return render_template("forgotpassword.html",info=info)


@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    token = request.args.get("token")
    info = request.args.get("info")
    if not token:
        return redirect(url_for("forgotpassword",info="Invalid reset link."))
    try:
        email = s.loads(token,salt="password-reset-salt",max_age=600)
    except SignatureExpired:
        return redirect(url_for("forgotpassword",info="Reset link expired. Please request a new link."))
    except Exception:
        return redirect(url_for("forgotpassword",info="Invalid reset link."))
    if request.method == "POST":
        newpassword = request.form.get("password", "")
        confirmpassword = request.form.get("confirm_password","")
        if newpassword != confirmpassword:
            return redirect(url_for("resetpassword",token=token,info="Passwords do not match."))
        password_pattern = ( r"^(?=.*[a-z])" r"(?=.*[A-Z])" r"(?=.*\d)" r"(?=.*[@$!%*?&])" r".{8,}$" )
        if not re.match(password_pattern, newpassword):
            return redirect(url_for("resetpassword",token=token,info=(
                        "Password must contain at least 8 characters, "
                        "one uppercase letter, one lowercase letter, "
                        "one number and one special character.")))
        hashed_password = bcrypt.hashpw( newpassword.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")
        cursor = db.cursor()
        cursor.execute(""" UPDATE users SET password = %s WHERE email = %s """, (hashed_password, email))
        db.commit()
        cursor.close()
        return redirect(url_for("login",info="Password reset successful. Please login."))
    return render_template("resetpassword.html",info=info,email=email)







@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login",info="You have been logged out."))




if __name__ == "__main__":
    app.run(debug=True)
