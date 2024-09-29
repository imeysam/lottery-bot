from database import get_db
from models import User, Child
from sqlalchemy.orm import Session


def get_user_by_chat_id(chat_id):
    db: Session = next(get_db())
    return db.query(User).filter(User.chat_id == chat_id).first()
