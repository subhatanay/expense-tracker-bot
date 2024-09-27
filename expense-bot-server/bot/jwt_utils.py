import jwt
import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Secret key for encoding and decoding JWT tokens
# It's best to set this as an environment variable for security purposes
SECRET_KEY = os.getenv('JWT_KEY', '#$@@$#$#$#gdhtt%$%=#%##$#')  
ALGORITHM = "HS256"  # Algorithm used for encoding

def generate_token(payload: Dict[str, Any], expires_in: int = 360000) -> str:
    # Copy the payload to avoid modifying the original
    payload_copy = payload.copy()

    # Add expiration time to payload
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    payload_copy.update({"exp": expiration_time})

    # Encode the token
    token = jwt.encode(payload_copy, SECRET_KEY, algorithm=ALGORITHM)

    # In PyJWT >= 2.0, jwt.encode returns a string directly
    return token

def decode_token(token: str) -> Dict[str, Any]: 
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        # Signature has expired
        raise jwt.ExpiredSignatureError("Token has expired.")
    except jwt.InvalidTokenError:
        # Token is invalid
        raise jwt.InvalidTokenError("Invalid token.")