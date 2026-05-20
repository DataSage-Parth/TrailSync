from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if "user_id" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        if role == "staff":
            return redirect(url_for("staff.staff_dashboard"))
        return redirect(url_for("user.user_dashboard"))
    return render_template("landing.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"].strip()
        pwd = request.form["password"]
        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, pwd):
            if user.status == "blacklisted":
                flash("Your account has been blacklisted. Contact admin.", "danger")
                return redirect(url_for("auth.login"))
            session["user_id"] = user.id
            session["role"] = user.role
            session["username"] = user.username
            flash(f"Welcome back, {user.full_name}!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            if user.role == "staff":
                return redirect(url_for("staff.staff_dashboard"))
            return redirect(url_for("user.user_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form["username"].strip()
        email = request.form["email"].strip()
        pwd = request.form["password"]
        fname = request.form["full_name"].strip()
        phone = request.form.get("phone", "").strip()
        if not uname or not email or not pwd or not fname:
            flash("All required fields must be filled.", "danger")
            return redirect(url_for("auth.register"))
        if len(uname) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return redirect(url_for("auth.register"))
        if len(pwd) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register"))
        if "@" not in email or "." not in email:
            flash("Invalid email address.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(username=uname).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))
        new_user = User(
            username=uname, email=email,
            password=generate_password_hash(pwd),
            full_name=fname, phone=phone, role="user",
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth.index"))
