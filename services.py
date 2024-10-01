from database import get_db
from models import User, Child
from sqlalchemy.orm import Session


def get_user_by_chat_id(chat_id):
    db: Session = next(get_db())
    return db.query(User).filter(User.chat_id == chat_id).first()


def convert_persian_to_english_numbers(input_str):
    # Create a mapping from Persian digits to English digits
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', 
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    
    # Replace each Persian digit with its English equivalent
    english_str = ''.join(persian_to_english.get(char, char) for char in input_str)
    
    return english_str