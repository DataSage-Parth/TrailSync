"""
Staff blueprint — dashboard, trek management, participants.
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

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/")
@role_required("staff")
def staff_dashboard():
    uid = session["user_id"]
    treks = Trek.query.filter_by(assigned_staff_id=uid).order_by(Trek.start_date).all()
    trek_participants = {}
    for t in treks:
        trek_participants[t.id] = Booking.query.filter_by(trek_id=t.id, status="Booked").count()
    return render_template("staff/dashboard.html", treks=treks, trek_participants=trek_participants)


@staff_bp.route("/trek/<int:tid>", methods=["GET", "POST"])
@role_required("staff")
def staff_trek_detail(tid):
    trek = Trek.query.filter_by(id=tid, assigned_staff_id=session["user_id"]).first()
    if not trek:
        flash("Trek not found or not assigned to you.", "danger")
        return redirect(url_for("staff.staff_dashboard"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_slots":
            new_avail = int(request.form["available_slots"])
            booked = Booking.query.filter_by(trek_id=tid, status="Booked").count()
            if new_avail < booked:
                flash(f"Cannot set below current bookings ({booked}).", "danger")
            else:
                trek.available_slots = new_avail
                trek.total_slots = new_avail + booked
                db.session.commit()
                flash("Slots updated.", "success")
        elif action == "update_status":
            new_status = request.form["status"]
            trek.status = new_status
            if new_status == "Completed":
                Booking.query.filter_by(trek_id=tid, status="Booked").update({"status": "Completed"})
            db.session.commit()
            flash("Status updated.", "success")
        return redirect(url_for("staff.staff_trek_detail", tid=tid))
    participants = (
        db.session.query(Booking, User)
        .join(User, Booking.user_id == User.id)
        .filter(Booking.trek_id == tid)
        .order_by(Booking.booking_date).all()
    )
    return render_template("staff/trek_detail.html", trek=trek, participants=participants)
