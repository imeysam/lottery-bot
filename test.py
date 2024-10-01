from dotenv import load_dotenv
from database import get_db
from models import User, Child
from sqlalchemy.orm import Session
import requests
from const import education_levels, genders, marital_statuses, photo_example_captions

load_dotenv()

from models import User
from services import get_user_by_chat_id, convert_persian_to_english_numbers

def get_user():
    user_id = 1
    return get_user_by_chat_id(chat_id=962527065)





if __name__ == "__main__":
    # Example usage
    input_string = "۱۲۳۴۵۶۷۸۹۰یی"
    converted_string = convert_persian_to_english_numbers(input_string)
    print(converted_string) 
    # try:
    #     print(int("۱"))
        
    # except:
    #     print("invalid")
    # user = get_user()
    # print(user)
    # print("\n".join(display_user_status_steps(user)))
    
