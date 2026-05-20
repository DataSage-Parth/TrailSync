from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
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

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@role_required("admin")
def admin_dashboard():
    stats = {
        "treks": Trek.query.count(),
        "users": User.query.filter_by(role="user").count(),
        "staff": User.query.filter_by(role="staff").count(),
        "bookings": Booking.query.count(),
        "open": Trek.query.filter_by(status="Open").count(),
        "completed": Trek.query.filter_by(status="Completed").count(),
    }
    recent_bookings = (
        db.session.query(Booking, User, Trek)
        .join(User, Booking.user_id == User.id)
        .join(Trek, Booking.trek_id == Trek.id)
        .order_by(Booking.booking_date.desc()).limit(5).all()
    )
    recent_treks = Trek.query.order_by(Trek.created_at.desc()).limit(5).all()
    
    # Chart Data Preparation
    import json
    popular_treks = []
    for t in Trek.query.all():
        b_count = Booking.query.filter_by(trek_id=t.id).count()
        popular_treks.append({"name": t.name, "count": b_count})
    popular_treks.sort(key=lambda x: x["count"], reverse=True)
    top_5 = popular_treks[:5]
    
    trek_chart_labels = [x["name"] for x in top_5]
    trek_chart_data = [x["count"] for x in top_5]
    
    booking_status_data = [
        Booking.query.filter_by(status="Booked").count(),
        Booking.query.filter_by(status="Completed").count(),
        Booking.query.filter_by(status="Cancelled").count()
    ]

    return render_template("admin/dashboard.html", stats=stats,
                           recent_bookings=recent_bookings, recent_treks=recent_treks,
                           trek_chart_labels=json.dumps(trek_chart_labels),
                           trek_chart_data=json.dumps(trek_chart_data),
                           booking_status_data=json.dumps(booking_status_data))


# ── Treks ────────────────────────────────────────────────────────────
@admin_bp.route("/treks")
@role_required("admin")
def admin_treks():
    q = request.args.get("q", "").strip()
    query = Trek.query
    if q:
        filters = [Trek.name.ilike(f"%{q}%"), Trek.location.ilike(f"%{q}%")]
        if q.isdigit():
            filters.append(Trek.id == int(q))
        query = query.filter(db.or_(*filters))
    treks = query.order_by(Trek.created_at.desc()).all()
    return render_template("admin/treks.html", treks=treks, q=q)


@admin_bp.route("/treks/add", methods=["GET", "POST"])
@role_required("admin")
def admin_add_trek():
    staff_list = User.query.filter_by(role="staff", status="active").all()
    if request.method == "POST":
        name = request.form["name"].strip()
        location = request.form["location"].strip()
        if not name or not location:
            flash("Trek name and location are required.", "danger")
            return redirect(url_for("admin.admin_add_trek"))
        try:
            slots = int(request.form["total_slots"])
            duration_days = int(request.form["duration_days"])
            price = float(request.form.get("price", 0))
            if slots <= 0 or duration_days <= 0 or price < 0:
                raise ValueError
        except ValueError:
            flash("Slots and duration must be positive integers, and price cannot be negative.", "danger")
            return redirect(url_for("admin.admin_add_trek"))
        
        trek = Trek(
            name=name,
            location=location,
            difficulty=request.form["difficulty"],
            duration_days=duration_days,
            total_slots=slots,
            available_slots=slots,
            assigned_staff_id=request.form.get("assigned_staff_id") or None,
            status=request.form.get("status", "Pending"),
            start_date=request.form.get("start_date") or None,
            end_date=request.form.get("end_date") or None,
            description=request.form.get("description", "").strip(),
            price=float(request.form.get("price", 0)),
            altitude=request.form.get("altitude", "").strip(),
        )
        db.session.add(trek)
        db.session.commit()
        flash("Trek created!", "success")
        return redirect(url_for("admin.admin_treks"))
    return render_template("admin/add_trek.html", staff_list=staff_list)


@admin_bp.route("/treks/<int:tid>/edit", methods=["GET", "POST"])
@role_required("admin")
def admin_edit_trek(tid):
    trek = Trek.query.get_or_404(tid)
    staff_list = User.query.filter_by(role="staff", status="active").all()
    if request.method == "POST":
        name = request.form["name"].strip()
        location = request.form["location"].strip()
        if not name or not location:
            flash("Trek name and location are required.", "danger")
            return redirect(url_for("admin.admin_edit_trek", tid=tid))
        try:
            new_total = int(request.form["total_slots"])
            duration_days = int(request.form["duration_days"])
            price = float(request.form.get("price", 0))
            if new_total <= 0 or duration_days <= 0 or price < 0:
                raise ValueError
        except ValueError:
            flash("Slots and duration must be positive integers, and price cannot be negative.", "danger")
            return redirect(url_for("admin.admin_edit_trek", tid=tid))

        booked = trek.total_slots - trek.available_slots
        new_avail = max(new_total - booked, 0)
        trek.name = name
        trek.location = location
        trek.difficulty = request.form["difficulty"]
        trek.duration_days = duration_days
        trek.total_slots = new_total
        trek.available_slots = new_avail
        trek.assigned_staff_id = request.form.get("assigned_staff_id") or None
        trek.status = request.form.get("status", "Pending")
        trek.start_date = request.form.get("start_date") or None
        trek.end_date = request.form.get("end_date") or None
        trek.description = request.form.get("description", "").strip()
        trek.price = float(request.form.get("price", 0))
        trek.altitude = request.form.get("altitude", "").strip()
        db.session.commit()
        flash("Trek updated!", "success")
        return redirect(url_for("admin.admin_treks"))
    return render_template("admin/edit_trek.html", trek=trek, staff_list=staff_list)


@admin_bp.route("/treks/<int:tid>/delete", methods=["POST"])
@role_required("admin")
def admin_delete_trek(tid):
    trek = Trek.query.get_or_404(tid)
    Booking.query.filter_by(trek_id=tid).delete()
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.", "info")
    return redirect(url_for("admin.admin_treks"))


# ── Staff ────────────────────────────────────────────────────────────
@admin_bp.route("/staff")
@role_required("admin")
def admin_staff():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="staff")
    if q:
        filters = [User.full_name.ilike(f"%{q}%"), User.username.ilike(f"%{q}%")]
        if q.isdigit():
            filters.append(User.id == int(q))
        query = query.filter(db.or_(*filters))
    staff = query.order_by(User.created_at.desc()).all()
    return render_template("admin/staff.html", staff=staff, q=q)


@admin_bp.route("/staff/add", methods=["GET", "POST"])
@role_required("admin")
def admin_add_staff():
    if request.method == "POST":
        uname = request.form["username"].strip()
        email = request.form["email"].strip()
        pwd = request.form["password"]
        fname = request.form["full_name"].strip()
        
        if not uname or not email or not pwd or not fname:
            flash("All required fields must be filled.", "danger")
            return redirect(url_for("admin.admin_add_staff"))
        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("admin.admin_add_staff"))
        if "@" not in email or "." not in email:
            flash("Invalid email format.", "danger")
            return redirect(url_for("admin.admin_add_staff"))

        if User.query.filter_by(username=uname).first():
            flash("Username taken.", "danger")
            return redirect(url_for("admin.admin_add_staff"))
        if User.query.filter_by(email=email).first():
            flash("Email taken.", "danger")
            return redirect(url_for("admin.admin_add_staff"))
        staff = User(
            username=uname, email=email,
            password=generate_password_hash(request.form["password"]),
            full_name=request.form["full_name"].strip(),
            phone=request.form.get("phone", "").strip(),
            role="staff",
            bio=request.form.get("bio", "").strip(),
        )
        db.session.add(staff)
        db.session.commit()
        flash("Staff member added!", "success")
        return redirect(url_for("admin.admin_staff"))
    return render_template("admin/add_staff.html")


@admin_bp.route("/staff/<int:sid>/remove", methods=["POST"])
@role_required("admin")
def admin_remove_staff(sid):
    staff = User.query.filter_by(id=sid, role="staff").first_or_404()
    Trek.query.filter_by(assigned_staff_id=sid).update({"assigned_staff_id": None})
    db.session.delete(staff)
    db.session.commit()
    flash("Staff removed.", "info")
    return redirect(url_for("admin.admin_staff"))


@admin_bp.route("/staff/<int:sid>/toggle", methods=["POST"])
@role_required("admin")
def admin_toggle_staff(sid):
    staff = User.query.get_or_404(sid)
    staff.status = "blacklisted" if staff.status == "active" else "active"
    db.session.commit()
    flash(f"Staff {'blacklisted' if staff.status == 'blacklisted' else 'activated'}.", "info")
    return redirect(url_for("admin.admin_staff"))


# ── Users ────────────────────────────────────────────────────────────
@admin_bp.route("/users")
@role_required("admin")
def admin_users():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="user")
    if q:
        filters = [User.full_name.ilike(f"%{q}%"), User.username.ilike(f"%{q}%")]
        if q.isdigit():
            filters.append(User.id == int(q))
        query = query.filter(db.or_(*filters))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, q=q)


@admin_bp.route("/users/<int:uid>/toggle", methods=["POST"])
@role_required("admin")
def admin_toggle_user(uid):
    user = User.query.get_or_404(uid)
    user.status = "blacklisted" if user.status == "active" else "active"
    db.session.commit()
    flash(f"User {'blacklisted' if user.status == 'blacklisted' else 'activated'}.", "info")
    return redirect(url_for("admin.admin_users"))


# ── Bookings ─────────────────────────────────────────────────────────
@admin_bp.route("/bookings")
@role_required("admin")
def admin_bookings():
    q = request.args.get("q", "").strip()
    query = db.session.query(Booking, User, Trek).join(User, Booking.user_id == User.id).join(Trek, Booking.trek_id == Trek.id)
    if q:
        filters = [User.full_name.ilike(f"%{q}%"), User.username.ilike(f"%{q}%"), Trek.name.ilike(f"%{q}%")]
        if q.isdigit():
            filters.append(Booking.id == int(q))
        query = query.filter(db.or_(*filters))
    bookings = query.order_by(Booking.booking_date.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings, q=q)
