# /app/utils/jwt_utils.py
import jwt
import datetime
from typing import Optional

# Secret key for encoding and decoding the JWT
SECRET_KEY = "7<Mad@h@V$123!0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set your expiry time for the token

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    """
    Create an access token with the provided data (user info).
    :param data: The data to encode into the token (e.g., username).
    :param expires_delta: Optional expiration time.
    :return: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Verify the provided token and return the decoded payload.
    :param token: The JWT token to verify
    :return: Decoded token payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
