"""
Alert Service
- Create DB alert records
- Send real-time Socket.IO push notifications
- Send email alerts via Flask-Mail
"""

from app import db, mail, socketio
from app.models import Alert, User
from flask_mail import Message
import os


def create_alert(user_id, transaction_ref, alert_type, message):
    """Persist an alert, push via WebSocket, and optionally email."""
    alert = Alert(
        user_id=user_id,
        transaction_ref=transaction_ref,
        alert_type=alert_type,
        message=message,
    )
    db.session.add(alert)
    db.session.commit()

    # Real-time push via Socket.IO
    _push_socket_alert(user_id, alert)

    # Email alert for high-severity types
    if alert_type in ("fraud_detected", "high_amount", "blocked"):
        _send_email_alert(user_id, alert)

    return alert


def _push_socket_alert(user_id, alert):
    """Emit alert to a user-specific Socket.IO room."""
    try:
        socketio.emit(
            "fraud_alert",
            alert.to_dict(),
            room=f"user_{user_id}",
        )
    except Exception as e:
        print(f"[SocketIO] Failed to push alert: {e}")


def _send_email_alert(user_id, alert):
    """Send fraud alert email to user."""
    try:
        user = User.query.get(user_id)
        if not user or not user.email:
            return

        mail_username = os.getenv("MAIL_USERNAME")
        if not mail_username:
            return  # Email not configured

        msg = Message(
            subject=f"[ALERT] Suspicious Activity Detected - {alert.alert_type.upper()}",
            sender=mail_username,
            recipients=[user.email],
        )
        msg.body = f"""
Hello {user.username},

We detected suspicious activity on your account.

Alert Type : {alert.alert_type}
Transaction : {alert.transaction_ref}
Details     : {alert.message}
Time        : {alert.created_at}

If this was not you, please contact support immediately.

— Fraud Detection Team
        """.strip()

        mail.send(msg)

        alert.sent_via_email = True
        db.session.commit()

    except Exception as e:
        print(f"[Email] Failed to send alert email: {e}")
