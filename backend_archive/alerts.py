from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models import Alert
from flask_socketio import join_room

alerts_bp = Blueprint("alerts", __name__)


# ────────────────────────────────────────────
# GET /api/alerts/  — get user's alerts
# ─────────────────────────────────────────────
@alerts_bp.route("/", methods=["GET"])
@jwt_required()
def get_alerts():
    user_id = int(get_jwt_identity())
    unread_only = request.args.get("unread", "false").lower() == "true"
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Alert.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)

    paginated = query.order_by(Alert.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "alerts": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "unread_count": Alert.query.filter_by(user_id=user_id, is_read=False).count(),
    }), 200


# ─────────────────────────────────────────────
# PUT /api/alerts/<id>/read
# ─────────────────────────────────────────────
@alerts_bp.route("/<int:alert_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(alert_id):
    user_id = int(get_jwt_identity())
    alert = Alert.query.get(alert_id)

    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    if alert.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    alert.is_read = True
    db.session.commit()
    return jsonify({"message": "Alert marked as read"}), 200


# ─────────────────────────────────────────────
# PUT /api/alerts/mark-all-read
# ─────────────────────────────────────────────
@alerts_bp.route("/mark-all-read", methods=["PUT"])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    Alert.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All alerts marked as read"}), 200


# ─────────────────────────────────────────────
# DELETE /api/alerts/<id>
# ─────────────────────────────────────────────
@alerts_bp.route("/<int:alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id):
    user_id = int(get_jwt_identity())
    alert = Alert.query.get(alert_id)

    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    if alert.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": "Alert deleted"}), 200


# ─────────────────────────────────────────────
# Socket.IO — client joins their personal room
# ─────────────────────────────────────────────
@socketio.on("join")
def handle_join(data):
    """Client sends: { user_id: 5 }"""
    user_id = data.get("user_id")
    if user_id:
        join_room(f"user_{user_id}")
        socketio.emit("joined", {"room": f"user_{user_id}"})
