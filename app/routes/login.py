# /app/routes/login.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import timedelta
from app.utils.jwt_utils import create_access_token

router = APIRouter()

# Define the request body format
class LoginRequest(BaseModel):
    username: str
    password: str

# Fake user database (replace with actual database logic)
fake_users_db = {
    "testuser": {"username": "testuser", "password": "password123"}  # Replace with hashed passwords
}

@router.post("/login")
def login(request: LoginRequest):
    user = fake_users_db.get(request.username)
    if user and user["password"] == request.password:  # Add your password hashing logic here
        # Create JWT token
        access_token = create_access_token(data={"sub": request.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
