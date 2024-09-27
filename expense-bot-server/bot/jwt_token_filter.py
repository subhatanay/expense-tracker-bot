from flask import Flask, request, jsonify
from functools import wraps
from jwt_utils import decode_token

app = Flask(__name__)

# Function to verify token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check if token is in request headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Assuming "Bearer <token>"

        # Return an error if no token is found
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            # Decode the token (assuming it's a JWT token)
            decoded = decode_token(token)
            request.user = decoded  # Attach decoded info to request for use in routes
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403

        return f(*args, **kwargs)
    
    return decorated_function