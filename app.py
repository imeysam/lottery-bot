from telebot import TeleBot
from dotenv import load_dotenv
import os
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from database import get_db
from models import User, Child
from sqlalchemy.orm import Session
import requests
from const import education_levels, genders, marital_statuses, photo_example_captions

load_dotenv()

TOKEN = os.getenv("TOKEN")
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
bot = TeleBot(TOKEN)



user_steps = User.steps()

children_steps = Child.steps()

def next_inline_button():
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_next = InlineKeyboardButton(text="گام بعد (skip) ⏮", callback_data="next_step")
    btn_show = InlineKeyboardButton(text="👀 نمایش کل اطلاعات", callback_data="btn_show")
    btn_edit = InlineKeyboardButton(text="📝 ویرایش از ابتدا", callback_data="btn_edit")
    # button_prev = InlineKeyboardButton(text="⏭ گام قبل (back)", callback_data="prev_step")
    inline_keyboard.add(button_next)
    inline_keyboard.add(btn_show, btn_edit)
    return inline_keyboard

def create_inline_keyboard(options):
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=level, callback_data=level) for level in options]
    inline_keyboard.add(*buttons)
    inline_keyboard.add(
        InlineKeyboardButton(text="مرحله بعد (skip) ⏮", callback_data="next_step"),
        # InlineKeyboardButton(text="⏭ گام قبل (back)", callback_data="prev_step")
    )
    inline_keyboard.add(
        InlineKeyboardButton(text="👀 نمایش کل اطلاعات", callback_data="btn_show"),
        InlineKeyboardButton(text="📝 ویرایش از ابتدا", callback_data="btn_edit")
    )
    return inline_keyboard


def show_user_info(user):
    messages = []
    # if user.step > user.last_step:
    #     messages.append("*ثبت نام شما تکمیل شده است.* \n")
    
    messages.append("*اطلاعات وارد شده:*")
    
    for step in user_steps.values():
        field_name = step.get('field_name')
        field_type = step.get('type')
        
        column_value = getattr(user, field_name, None)
        if field_name == 'spouse_first_name' and column_value is not None:
            messages.append("\n*همسر:*")
        if column_value is not None:
            if field_type == "photo":
                column_value = "✅"
            messages.append(f"*{step.get('title')}:* {column_value}")
            
    if user is not None:
        db: Session = next(get_db())
        children = db.query(Child).filter(Child.user_id == user.id).all()
        
        for child in children:
            if child.step > 1:
                messages.append(f"\n*فرزند {child.order_no}:*")
            for step in children_steps.values():
                field_name = step.get('field_name')
                field_type = step.get('type')
                column_value = getattr(child, field_name, None)
                if column_value is not None:
                    if field_type == "photo":
                        column_value = "✅"
                    messages.append(f"*{step.get('title')}:* {column_value}")
            
            
    if len(messages) > 1:
        bot.send_message(
            chat_id=user.chat_id,
            text="\n".join(messages),
            parse_mode= 'Markdown'
        )


def get_info_prompt(user):
    show_user_info(user=user)
    
    if user.is_completed == False:
        if user.step <= user.last_step:
            current_step = user_steps.get(user.step)
            if current_step:
                current_step_type = current_step.get('type')
                text = f"*{current_step.get('message')}* \n"
                    
                if current_step.get('example'):
                    text = f"{text}\nمانند: {current_step.get('example')}"
                if current_step_type == "string":
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=next_inline_button()
                    )
                elif current_step_type == "photo":
                    # text = r"*عکس*:/\nنمونه تصاویر \/photo\_example"
                    # bot.send_message(user.chat_id, text, parse_mode="MarkdownV2")
                    text = f"*{current_step.get('message')}*"
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=next_inline_button()
                    )
                    bot.send_message(
                        chat_id=user.chat_id,
                        text="نمونه تصاویر /photo_example",
                    )
                elif current_step_type == "dropdown":
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=create_inline_keyboard(current_step.get('choices', []))
                    )
        elif user.has_child:
            db: Session = next(get_db())
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
            if child is not None:
                current_step = children_steps.get(child.step)
                if current_step:
                    current_step_type = current_step.get('type')

                    text = f"*{current_step.get('message')} فرزند {child.order_no}* \n"
                    if current_step.get('example'):
                        text = f"{text}\nمانند: {current_step.get('example')}"
                    if current_step_type == "string":
                        bot.send_message(
                            chat_id=user.chat_id,
                            text=text,
                            parse_mode='Markdown',
                            reply_markup=next_inline_button()
                        )
                    elif current_step_type == "photo":
                        text = f"*{current_step.get('message')}*"
                        bot.send_message(
                            chat_id=user.chat_id,
                            text=text,
                            parse_mode='Markdown',
                            reply_markup=next_inline_button()
                        )
                        bot.send_message(
                            chat_id=user.chat_id,
                            text="نمونه تصاویر /photo_example",
                        )
                    elif current_step_type == "dropdown":
                        bot.send_message(
                            chat_id=user.chat_id,
                            text=text,
                            parse_mode='Markdown',
                            reply_markup=create_inline_keyboard(current_step.get('choices', []))
                        )


@bot.message_handler(commands=['start', 'follow'])
def start_message(message: Message):
    user_chat_id = message.chat.id
    print(message.chat)
    markup = InlineKeyboardMarkup()
    
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.chat_id == user_chat_id).first()
    if existing_user is not None:
        btn_show = InlineKeyboardButton(
            text=f"{existing_user.icon} نمایش اطلاعات", callback_data="btn_show"
        )
        btn_edit = InlineKeyboardButton(
            text="📝 ویرایش", callback_data="btn_edit"
        )
        btn_next = InlineKeyboardButton(
            text="🚀 ادامه فرآیند ثبت‌نام", callback_data="get_info"
        )
        btn_photos = InlineKeyboardButton(
            text="🖼 تصاویر ارسال شده", callback_data="show_photos"
        )
        markup.add(btn_next)
        markup.add(btn_edit, btn_show)
        markup.add(btn_photos)
    else:
        db: Session = next(get_db())
        existing_user = User(chat_id=user_chat_id, username=message.chat.username)
        db.add(existing_user)
        db.commit()
        btn_start = InlineKeyboardButton(
            text="✈️ بزن بریم شروع کنیم", callback_data="get_info"
        )
        markup.add(btn_start)
    
    btn_photo_example = InlineKeyboardButton(
        text="📸 نمونه تصاویر مورد تایید", callback_data="photo_example"
    )
    markup.add(btn_photo_example)
        
    bot.send_message(
        chat_id=user_chat_id,
        text="*ثبت‌نام لاتاری گرین کارت آمریکا* 🇺🇸✍🏼 \n\n لطفاً از طریق این 👇 داشبورد ادامه بدید\n",
        reply_markup=markup,
        parse_mode='Markdown'
    )
    


def show_photo_examples(chat_id):
    media = [
        InputMediaPhoto(open('img_samples/1.png', 'rb')),
        InputMediaPhoto(open('img_samples/2.png', 'rb')),
        InputMediaPhoto(open('img_samples/3.png', 'rb')),
        InputMediaPhoto(open('img_samples/4.png', 'rb')),
        InputMediaPhoto(open('img_samples/5.png', 'rb')),
        InputMediaPhoto(open('img_samples/6.png', 'rb')),
    ]

    media[0].caption = photo_example_captions
    bot.send_media_group(chat_id, media)



@bot.message_handler(commands=['photo_example'])
def photo_example_command(message: Message):
    user_chat_id = message.chat.id
    show_photo_examples(chat_id=user_chat_id)

@bot.callback_query_handler(func=lambda call: call.data == "photo_example")
def photo_example_call(call):
    user_chat_id = call.message.chat.id
    show_photo_examples(chat_id=user_chat_id)


image_folder_name = 'user_images'
image_folder_path = os.path.join(ROOT_PATH, image_folder_name)
os.makedirs(image_folder_path, exist_ok=True)
# if not os.path.exists(image_folder):
#     os.makedirs(image_folder)

    
@bot.callback_query_handler(func=lambda call: call.data == "btn_show")
def show_info(call):
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.chat_id == user_chat_id).first()
    bot.answer_callback_query(call.id)
    show_user_info(user=existing_user)
    

@bot.callback_query_handler(func=lambda call: call.data == "btn_edit")
def edit_info(call):
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    user.is_completed = False
    user.step = 1
    db.commit()
    bot.answer_callback_query(call.id)
    get_info_prompt(user=user)


@bot.callback_query_handler(func=lambda call: call.data == "next_step")
def next_info(call):
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    if user.is_completed == False:
        if user.step <= user.last_step:
            user.step += 1
            db.commit()
        elif user.has_child:
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
            if child is not None and not child.is_steps_finished:
                child.step += 1
                db.commit()
            
    bot.answer_callback_query(call.id)
    get_info_prompt(user=user)


# @bot.callback_query_handler(func=lambda call: call.data == "prev_step")
# def prev_info(call):
#     user_chat_id = call.message.chat.id
#     db: Session = next(get_db())
#     user = db.query(User).filter(User.chat_id == user_chat_id).first()
#     if user.is_completed == False:
#         child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
        
#         if user.step > 1:
#             user.step = max([user.step-1, 1])
#             db.commit()
#         elif user.has_child:
            
#             if child is not None and not child.step > 1:
#                 child.step = max([child.step-1, 1])
#                 db.commit()
                
#     # user.step -= 1
#     # if(user.step < 1):
#     #     user.step = 1
#     # db.commit()
#     bot.answer_callback_query(call.id)
#     get_info_prompt(user=user)


@bot.callback_query_handler(func=lambda call: call.data == "get_info")
def get_info(call):
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.chat_id == user_chat_id).first()
    bot.answer_callback_query(call.id)
    get_info_prompt(user=existing_user)
        


@bot.callback_query_handler(func=lambda call: call.data == "show_photos")
def show_photos(call):
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    count = 0
    if user is not None:
        if user.photo is not None:
            print(user.photo)
            media = [
                InputMediaPhoto(open(user.photo, 'rb')),
            ]
            media[0].caption = user.first_name if user.first_name is not None else "تصویر شما"
            bot.send_media_group(user_chat_id, media)
            count += 1
            
        if user.spouse_photo is not None:
            media = [InputMediaPhoto(open(user.spouse_photo, 'rb'))]
            media[0].caption = user.spouse_first_name if user.spouse_first_name is not None else "تصویر همسر"
            bot.send_media_group(user_chat_id, media)
            count += 2
            
        if user.has_child: 
            children = db.query(Child).filter(Child.user_id == user.id).all()
            for child in children:
                if child.photo is not None:
                    media = [InputMediaPhoto(open(child.photo, 'rb'))]
                    media[0].caption = child.first_name if child.first_name is not None else f"تصویر فرزند {child.order_no}"
                    bot.send_media_group(user_chat_id, media)
                    count += 1
    if count < 1:
        bot.send_message(
            chat_id=user_chat_id,
            text="⚠️ تصویری وجود ندارد.",
        )
    
    # bot.answer_callback_query(call.id)
        
 
def get_photo(message, user, prefix = "_self"):
     # Get the file ID of the image (Telegram stores multiple sizes, we take the largest one)
    file_id = message.photo[-1].file_id
    
    # Get the file info (file path)
    file_info = bot.get_file(file_id)
    
    # Download the file from the Telegram servers
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
    downloaded_file = requests.get(file_url)
    
    # Create a filename (e.g., "image_<user_id>_<message_id>.jpg")
    file_name = f'{user.chat_id}_{prefix}_{message.message_id}.jpg'
    file_path = os.path.join(image_folder_name, file_name)
    
    # Save the image to the folder
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file.content)
        
    return file_path


@bot.message_handler(content_types=['photo'])
def store_photo(message):
    user_chat_id = message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    if user.is_completed == False:
        if user.step <= user.last_step:
            field_name = user_steps.get(user.step).get("field_name")
            if field_name in ["photo", "spouse_photo"]:
                field_name_fa = "شما" if field_name == "photo" else "همسر شما"
                photo_prefix = "_self" if field_name == "photo" else "_spouse"
                photo_path = get_photo(message=message, user=user, prefix=photo_prefix)
                setattr(user, field_name, photo_path)
                user.step += 1
                db.commit()
                bot.reply_to(message, f"تصویر {field_name_fa} با موفقیت ذخیره شد.")
                get_info_prompt(user=user)
                return
        elif user.has_child:
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
            if child is not None:
                photo_path = get_photo(message=message, user=user, prefix=f"_child_{child.order_no}")
                child.photo = photo_path
                user.step += 1
                db.commit()
                bot.reply_to(message, f"تصویر فرزند {child.order_no} با موفقیت ذخیره شد.")
                get_info_prompt(user=user)
                return
    
    bot.reply_to(message, "امکان ثبت تصویر وجود ندارد.")
    get_info_prompt(user=user)
    
   
    
    # Notify the user that the image has been saved
    # bot.reply_to(message, f"Image saved as {file_name} in folder {image_folder_name}.")

   

@bot.message_handler(func=lambda message: True)
def store_text_info(message):
    user_chat_id = message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    if user.is_completed == False:
        if user.step <= user.last_step:
            field_name = user_steps.get(user.step).get("field_name")
            setattr(user, field_name, message.text)
            
            if field_name == 'children_count':
                db.query(Child).filter(Child.user_id == user.id).delete()
                children_count = int(message.text)
                children = [Child(order_no=i+1) for i in range(children_count)]
                user.children.extend(children)
            
            user.step += 1
            db.commit()
        elif user.has_child:
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
            if child is not None:
                field_name = children_steps.get(child.step).get("field_name")
                setattr(child, field_name, message.text)
                if child.is_steps_finished:
                    child.is_completed = True
                else:    
                    child.step += 1
                db.commit()
        
        if user.step >= user.last_step:
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).count()
            if child == 0:
                user.is_completed = True
                db.commit()
                

        get_info_prompt(user=user)
            
    
    
    
    
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chosen_option = call.data  # This is the callback_data from the button
    user_chat_id = call.message.chat.id
    db: Session = next(get_db())
    user = db.query(User).filter(User.chat_id == user_chat_id).first()
    
    if user.is_completed == False:
        if user.step <= user.last_step:
            if chosen_option in education_levels:
                user.education_level = call.data
                user.step += 1
                db.commit()
            elif chosen_option in genders:
                user.gender = call.data
                user.step += 1
                db.commit()
            elif chosen_option in marital_statuses:
                user.marital_status = call.data
                user.step += 1
                db.commit()
        elif user.has_child:
            child = db.query(Child).filter(Child.user_id == user.id, Child.is_completed == False).first()
            if child is not None:
                if chosen_option in education_levels:
                    child.education_level = call.data
                    child.step += 1
                    db.commit()
                elif chosen_option in genders:
                    child.gender = call.data
                    child.step += 1
                    db.commit()
    
    get_info_prompt(user=user)
    
        

if __name__ == "__main__":
    from models import Base
    from database import engine
    Base.metadata.create_all(bind=engine)
    
    bot.polling()
