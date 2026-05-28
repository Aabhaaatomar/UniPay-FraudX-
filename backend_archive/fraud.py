import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from app.models import Transaction, FraudReport, User
from app.services.fraud_detector import analyze_transaction
from app.models import Blocklist

fraud_bp = Blueprint("fraud", __name__)


def _require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return None, (jsonify({"error": "Admin access required"}), 403)
    return user, None


# ─────────────────────────────────────────────
# POST /api/fraud/report
# Report a transaction as fraudulent (manual)
# ────────────────────────────────────────────
@fraud_bp.route("/report", methods=["POST"])
@jwt_required()
def report_fraud():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    transaction_id = data.get("transaction_id")
    reason = data.get("reason", "")

    tx = Transaction.query.filter_by(transaction_id=transaction_id).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
    if tx.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    report = FraudReport(
        transaction_id=tx.id,
        reported_by=user_id,
        reason=reason,
        ml_score=tx.fraud_score,
        status="open",
    )
    tx.is_fraud = True
    tx.status = "flagged"

    db.session.add(report)
    db.session.commit()

    return jsonify({
        "message": "Fraud report submitted",
        "report": report.to_dict(),
    }), 201


# ─────────────────────────────────────────────
# GET /api/fraud/reports  (admin)
# ─────────────────────────────────────────────
@fraud_bp.route("/reports", methods=["GET"])
@jwt_required()
def list_fraud_reports():
    _, err = _require_admin()
    if err:
        return err

    status_filter = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = FraudReport.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    paginated = query.order_by(FraudReport.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "reports": [r.to_dict() for r in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
    }), 200


# ─────────────────────────────────────────────
# PUT /api/fraud/reports/<id>/review  (admin)
# ─────────────────────────────────────────────
@fraud_bp.route("/reports/<int:report_id>/review", methods=["PUT"])
@jwt_required()
def review_report(report_id):
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json()
    report = FraudReport.query.get(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404

    new_status = data.get("status", "reviewed")
    if new_status not in ("reviewed", "closed"):
        return jsonify({"error": "Invalid status. Use 'reviewed' or 'closed'"}), 400

    report.status = new_status
    report.reviewed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Report updated", "report": report.to_dict()}), 200


# ─────────────────────────────────────────────
# POST /api/fraud/analyze  (re-analyze a transaction)
# ─────────────────────────────────────────────
@fraud_bp.route("/analyze/<string:transaction_id>", methods=["POST"])
@jwt_required()
def re_analyze(transaction_id):
    _, err = _require_admin()
    if err:
        return err

    tx = Transaction.query.filter_by(transaction_id=transaction_id).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    from datetime import timedelta
    from app.models import Blocklist
    blocklist_values = {b.value for b in Blocklist.query.all()}
    from app.routes.transactions import _get_known_devices
    known_devices = _get_known_devices(tx.user_id)

    ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
    recent_txns = Transaction.query.filter(
        Transaction.user_id == tx.user_id,
        Transaction.created_at >= ten_min_ago,
    ).all()

    result = analyze_transaction(tx, recent_txns, blocklist_values, known_devices)

    tx.is_fraud = result["is_fraud"]
    tx.fraud_score = result["fraud_score"]
    db.session.commit()

    return jsonify({"transaction_id": transaction_id, "analysis": result}), 200


# ─────────────────────────────────────────────
# GET /api/fraud/stats  (admin)
# ─────────────────────────────────────────────
@fraud_bp.route("/stats", methods=["GET"])
@jwt_required()
def fraud_stats():
    _, err = _require_admin()
    if err:
        return err

    total_tx = Transaction.query.count()
    fraud_tx = Transaction.query.filter_by(is_fraud=True).count()
    blocked_tx = Transaction.query.filter_by(status="blocked").count()
    open_reports = FraudReport.query.filter_by(status="open").count()

    return jsonify({
        "total_transactions": total_tx,
        "fraud_detected": fraud_tx,
        "blocked_transactions": blocked_tx,
        "open_reports": open_reports,
        "fraud_rate_percent": round((fraud_tx / total_tx * 100) if total_tx else 0, 2),
    }), 200
