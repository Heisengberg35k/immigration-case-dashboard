from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/test", methods=["GET"])
def auth_test():
    return jsonify({"message": "Auth routes working"}), 200