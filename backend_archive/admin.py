from flask import Blueprint, request, jsonify
from app.services.fraud_detector import get_dataset_info
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Transaction, Blocklist, Alert

admin_bp = Blueprint("admin", __name__)


def _require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return None, (jsonify({"error": "Admin access required"}), 403)
    return user, None


# ─────────────────────────────────────────────
# GET /api/admin/users
# ─────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    _, err = _require_admin()
    if err:
        return err

    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


# ────────────────────────────────────────────
# PUT /api/admin/users/<id>/toggle-active
# ─────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["PUT"])
@jwt_required()
def toggle_user_active(user_id):
    _, err = _require_admin()
    if err:
        return err

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({"message": f"User {'activated' if user.is_active else 'deactivated'}", "user": user.to_dict()}), 200


# ─────────────────────────────────────────────
# PUT /api/admin/users/<id>/role
# ─────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@jwt_required()
def update_role(user_id):
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json()
    role = data.get("role")
    if role not in ("user", "admin"):
        return jsonify({"error": "Role must be 'user' or 'admin'"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = role
    db.session.commit()
    return jsonify({"message": "Role updated", "user": user.to_dict()}), 200


# ─────────────────────────────────────────────
# GET /api/admin/transactions  — all transactions
# ─────────────────────────────────────────────
@admin_bp.route("/transactions", methods=["GET"])
@jwt_required()
def all_transactions():
    _, err = _require_admin()
    if err:
        return err

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 30, type=int)
    fraud_only = request.args.get("fraud_only", "false").lower() == "true"

    query = Transaction.query
    if fraud_only:
        query = query.filter_by(is_fraud=True)

    paginated = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "transactions": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
    }), 200


# ─────────────────────────────────────────────
# GET /api/admin/blocklist
# ─────────────────────────────────────────────
@admin_bp.route("/blocklist", methods=["GET"])
@jwt_required()
def get_blocklist():
    _, err = _require_admin()
    if err:
        return err

    entries = Blocklist.query.all()
    return jsonify({"blocklist": [e.to_dict() for e in entries]}), 200


# ─────────────────────────────────────────────
# POST /api/admin/blocklist  — add IP or device
# ─────────────────────────────────────────────
@admin_bp.route("/blocklist", methods=["POST"])
@jwt_required()
def add_to_blocklist():
    admin, err = _require_admin()
    if err:
        return err

    data = request.get_json()
    value = data.get("value", "").strip()
    block_type = data.get("block_type")  # ip | device
    reason = data.get("reason", "")

    if not value or block_type not in ("ip", "device"):
        return jsonify({"error": "value and block_type (ip|device) are required"}), 400

    if Blocklist.query.filter_by(value=value).first():
        return jsonify({"error": "Already in blocklist"}), 409

    entry = Blocklist(value=value, block_type=block_type, reason=reason, added_by=admin.id)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Added to blocklist", "entry": entry.to_dict()}), 201


# ─────────────────────────────────────────────
# DELETE /api/admin/blocklist/<id>
# ─────────────────────────────────────────────
@admin_bp.route("/blocklist/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def remove_from_blocklist(entry_id):
    _, err = _require_admin()
    if err:
        return err

    entry = Blocklist.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Removed from blocklist"}), 200


# ─────────────────────────────────────────────
# GET /api/admin/dashboard
# ─────────────────────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    _, err = _require_admin()
    if err:
        return err

    total_users = User.query.count()
    total_tx = Transaction.query.count()
    fraud_tx = Transaction.query.filter_by(is_fraud=True).count()
    blocked_tx = Transaction.query.filter_by(status="blocked").count()
    unread_alerts = Alert.query.filter_by(is_read=False).count()
    blocklist_count = Blocklist.query.count()

    return jsonify({
        "total_users": total_users,

        "total_transactions": total_tx,
        "fraud_transactions": fraud_tx,
        "blocked_transactions": blocked_tx,
        "unread_alerts": unread_alerts,
        "blocklist_entries": blocklist_count,
        "fraud_rate_percent": round((fraud_tx / total_tx * 100) if total_tx else 0, 2),
    }), 200


# ─────────────────────────────────────────────
# GET /api/admin/dataset-info
# ─────────────────────────────────────────────
@admin_bp.route("/dataset-info", methods=["GET"])
@jwt_required()
def dataset_info():
    _, err = _require_admin()
    if err:
        return err
    return jsonify(get_dataset_info()), 200
