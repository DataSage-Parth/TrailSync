"""
User (Trekker) blueprint — dashboard, trek browsing, bookings, history, profile.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Trek, Booking
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*a, **kw):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.index"))
        return f(*a, **kw)
    return decorated

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        @login_required
        def decorated(*a, **kw):
            if session.get("role") not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for("auth.index"))
            return f(*a, **kw)
        return decorated
    return wrapper

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard")
@role_required("user")
def user_dashboard():
    uid = session["user_id"]
    open_treks = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).order_by(Trek.start_date).limit(6).all()
    my_bookings = (
        db.session.query(Booking, Trek)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.user_id == uid, Booking.status == "Booked")
        .order_by(Booking.booking_date.desc()).all()
    )
    stats = {
        "total_bookings": Booking.query.filter_by(user_id=uid).count(),
        "active": Booking.query.filter_by(user_id=uid, status="Booked").count(),
        "completed": Booking.query.filter_by(user_id=uid, status="Completed").count(),
    }
    return render_template("user/dashboard.html", open_treks=open_treks,
                           my_bookings=my_bookings, stats=stats)


@user_bp.route("/treks")
@role_required("user")
def user_treks():
    query = Trek.query.filter(Trek.status.in_(["Open", "Approved"]))
    diff = request.args.get("difficulty", "")
    loc = request.args.get("location", "").strip()
    search = request.args.get("search", "").strip()
    if diff:
        query = query.filter_by(difficulty=diff)
    if loc:
        query = query.filter(Trek.location.ilike(f"%{loc}%"))
    if search:
        query = query.filter(db.or_(Trek.name.ilike(f"%{search}%"), Trek.location.ilike(f"%{search}%")))
    treks = query.order_by(Trek.start_date).all()
    locations = db.session.query(Trek.location).filter(Trek.status.in_(["Open", "Approved"])).distinct().order_by(Trek.location).all()
    return render_template("user/treks.html", treks=treks, locations=[l[0] for l in locations],
                           filters={"difficulty": diff, "location": loc, "search": search})


@user_bp.route("/treks/<int:tid>")
@role_required("user")
def user_trek_detail(tid):
    trek = Trek.query.get_or_404(tid)
    uid = session["user_id"]
    already_booked = Booking.query.filter_by(user_id=uid, trek_id=tid, status="Booked").first()
    
    return render_template("user/trek_detail.html", trek=trek, already_booked=bool(already_booked))

@user_bp.route("/treks/<int:tid>/book", methods=["POST"])
@role_required("user")
def user_book_trek(tid):
    trek = Trek.query.get_or_404(tid)
    if trek.status not in ("Open", "Approved"):
        flash("This trek is not available for booking.", "warning")
        return redirect(url_for("user.user_trek_detail", tid=tid))
    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("user.user_trek_detail", tid=tid))
    if Booking.query.filter_by(user_id=session["user_id"], trek_id=tid, status="Booked").first():
        flash("You already booked this trek.", "warning")
        return redirect(url_for("user.user_trek_detail", tid=tid))
    booking = Booking(user_id=session["user_id"], trek_id=tid, status="Booked")
    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()
    flash("Trek booked successfully!", "success")
    return redirect(url_for("user.user_bookings"))


@user_bp.route("/bookings")
@role_required("user")
def user_bookings():
    bookings = (
        db.session.query(Booking, Trek)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.user_id == session["user_id"])
        .order_by(Booking.booking_date.desc()).all()
    )
    return render_template("user/bookings.html", bookings=bookings)


@user_bp.route("/bookings/<int:bid>/cancel", methods=["POST"])
@role_required("user")
def user_cancel_booking(bid):
    booking = Booking.query.filter_by(id=bid, user_id=session["user_id"]).first()
    if booking and booking.status == "Booked":
        booking.status = "Cancelled"
        trek = Trek.query.get(booking.trek_id)
        trek.available_slots += 1
        db.session.commit()
        flash("Booking cancelled.", "info")
    return redirect(url_for("user.user_bookings"))


@user_bp.route("/history")
@role_required("user")
def user_history():
    history = (
        db.session.query(Booking, Trek)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.user_id == session["user_id"],
                Booking.status.in_(["Completed", "Cancelled"]))
        .order_by(Booking.booking_date.desc()).all()
    )
    return render_template("user/history.html", history=history)


@user_bp.route("/profile", methods=["GET", "POST"])
@role_required("user")
def user_profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        fname = request.form["full_name"].strip()
        email = request.form["email"].strip()
        
        if not fname or not email:
            flash("Full name and email are required.", "danger")
            return redirect(url_for("user.user_profile"))
        if "@" not in email or "." not in email:
            flash("Invalid email format.", "danger")
            return redirect(url_for("user.user_profile"))
            
        existing_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_email:
            flash("Email is already in use by another account.", "danger")
            return redirect(url_for("user.user_profile"))
            
        user.full_name = fname
        user.phone = request.form.get("phone", "").strip()
        user.bio = request.form.get("bio", "").strip()
        user.email = email
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("user.user_profile"))
    return render_template("user/profile.html", user=user)
