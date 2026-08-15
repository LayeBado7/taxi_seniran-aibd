from .realtime import emit_event

def notify_user(user_id, event, payload):
    """Real-time notification boundary; FCM can be added without changing business routes."""
    emit_event(event, {"user_id": user_id, **payload})
