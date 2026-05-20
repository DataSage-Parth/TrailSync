from flask import Blueprint, jsonify, request
from models import db, Trek, User, Booking

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/treks", methods=["GET"])
def get_treks():
    treks = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).all()
    result = []
    for t in treks:
        result.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "difficulty": t.difficulty,
            "duration_days": t.duration_days,
            "status": t.status,
            "price": t.price,
            "available_slots": t.available_slots
        })
    return jsonify(result), 200

@api_bp.route("/treks/<int:tid>", methods=["GET"])
def get_trek(tid):
    t = Trek.query.get(tid)
    if not t:
        return jsonify({"error": "Trek not found"}), 404
    return jsonify({
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration_days": t.duration_days,
        "status": t.status,
        "price": t.price,
        "description": t.description,
        "available_slots": t.available_slots
    }), 200

@api_bp.route("/users/<int:uid>", methods=["GET"])
def get_user(uid):
    u = User.query.get(uid)
    if not u:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": u.id,
        "username": u.username,
        "full_name": u.full_name,
        "role": u.role,
        "status": u.status
    }), 200

@api_bp.route("/bookings/<int:bid>", methods=["GET"])
def get_booking(bid):
    b = Booking.query.get(bid)
    if not b:
        return jsonify({"error": "Booking not found"}), 404
    return jsonify({
        "id": b.id,
        "user_id": b.user_id,
        "trek_id": b.trek_id,
        "status": b.status,
        "booking_date": b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else None
    }), 200
