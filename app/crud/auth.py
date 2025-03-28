from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import AuthRequest
import bcrypt


def authenticate_user(db: Session, auth_data: AuthRequest) -> bool:
    user = db.query(User).filter(User.name == auth_data.name).first()
    if not user:
        return False
    return bcrypt.checkpw(auth_data.password.encode(), user.password.encode())
