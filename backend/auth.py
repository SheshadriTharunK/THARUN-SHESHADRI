import hashlib
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User


SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    # Pre-hash using SHA256
    password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=100)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         print("Decoded JWT payload:", payload)
         email = payload.get("sub")
         user = db.query(User).filter(User.email == email).first()
         if user is None:
                raise HTTPException(status_code=401, detail="User not found")
         return email 
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")