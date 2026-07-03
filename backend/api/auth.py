from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)


def _default_users() -> dict:
    return {
        "admin": {
            "username": "admin",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin",
            "display_name": "Project Admin",
        },
        "user": {
            "username": "user",
            "password_hash": generate_password_hash("user123"),
            "role": "user",
            "display_name": "Normal User",
        },
    }


USERS = _default_users()


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token")


def create_token(user: dict) -> str:
    return _serializer().dumps(
        {
            "username": user["username"],
            "role": user["role"],
            "display_name": user["display_name"],
        }
    )


def user_from_token() -> dict | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return None

    try:
        return _serializer().loads(token, max_age=60 * 60 * 24)
    except (BadSignature, SignatureExpired):
        return None


def current_user():
    return session.get("user") or user_from_token()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return jsonify({"message": "Login required"}), 401
        return view(*args, **kwargs)

    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return jsonify({"message": "Login required"}), 401
            if user["role"] != role:
                return jsonify({"message": "You do not have access to this resource"}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username", "").strip().lower()
    password = payload.get("password", "")

    user = USERS.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid username or password"}), 401

    session.clear()
    session["user"] = {
        "username": user["username"],
        "role": user["role"],
        "display_name": user["display_name"],
    }
    return jsonify({"user": session["user"], "token": create_token(session["user"])})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user": current_user()})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/admin/overview")
@role_required("admin")
def admin_overview():
    return jsonify(
        {
            "message": "Admin access granted",
            "next_modules": [
                "manage users",
                "monitor scrapers",
                "review model runs",
                "publish dashboard insights",
            ],
        }
    )
