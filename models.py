from database import Base
from typing import List
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from const import education_levels, genders, marital_statuses, photo_example_captions
from enum import Enum
from database import get_db


class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    is_completed = Column(Boolean, default=False)
    step = Column(Integer, default=1)
    order_no = Column(Integer, default=1)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    birth_place_country = Column(String, nullable=True)
    birth_place_city = Column(String, nullable=True)
    photo = Column(String, nullable=True)

    user = relationship("User", back_populates="children")

    @property
    def is_steps_finished(self):
        return self.step >= 8
    
    def steps():
        return {
            1: {
                "field_name": "first_name",
                "title": "نام",
                "message": "نام (انگلیسی):",
                "type": "string",
                "example": "kambiz",
            },
            2: {
                "field_name": "last_name",
                "title": "نام خانوادگی",
                "message": "نام خانوادگی (انگلیسی):",
                "type": "string",
                "example": "barzegar",
            },
            3: {
                "field_name": "education_level",
                "title": "آخرین مدرک تحصیلی",
                "message": "آخرین مدرک تحصیلی:",
                "type": "dropdown",
                "choices": education_levels,
            },
            4: {
                "field_name": "gender",
                "title": "جنسیت",
                "message": "جنسیت:",
                "type": "dropdown",
                "choices": genders,
            },
            5: {
                "field_name": "birth_date",
                "title": "تاریخ تولد",
                "message": "تاریخ تولد:",
                "type": "string",
                "example": "۱ فروردین ۱۴۰۲",
            },
            6: {
                "field_name": "photo",
                "title": "عکس",
                "message": "عکس:",
                "type": "photo",
                "example": photo_example_captions,
            },
            7: {
                "field_name": "birth_place_country",
                "title": "کشور تولد",
                "message": "کشور تولد:",
                "type": "string",
                "example": "ایران",
            },
            8: {
                "field_name": "birth_place_city",
                "title": "شهر تولد",
                "message": "شهر تولد:",
                "type": "string",
                "example": "تهران",
            },
        }


class UserStatus(Enum):
    COMPLETING = 10
    AWAINTING_CONFIRMATION = 20
    AWAINTING_PAYMENT = 30
    AWAINTING_REGISTRATION = 40
    FINALIZED = 50

user_status_translations = {
    UserStatus.COMPLETING: "تکمیل اطلاعات",
    UserStatus.AWAINTING_CONFIRMATION: "تایید اطلاعات",
    UserStatus.AWAINTING_PAYMENT: "پرداخت",
    UserStatus.AWAINTING_REGISTRATION: "ثبت در سامانه لاتاری",
    UserStatus.FINALIZED: "ثبت‌نام شده",
}

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    is_completed = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    status = Column(Integer, nullable=False, default=UserStatus.COMPLETING.value)
    step = Column(Integer, default=1)
    tracking_code = Column(String, nullable=True)
    
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    birth_place_country = Column(String, nullable=True)
    birth_place_city = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    children_count = Column(Integer, default=0)
    mobile_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    living_country = Column(String, nullable=True)
    living_province = Column(String, nullable=True)
    living_city = Column(String, nullable=True)
    living_postal_no = Column(String, nullable=True)
    living_address = Column(String, nullable=True)

    spouse_first_name = Column(String, nullable=True)
    spouse_last_name = Column(String, nullable=True)
    spouse_education_level = Column(String, nullable=True)
    spouse_gender = Column(String, nullable=True)
    spouse_birth_date = Column(String, nullable=True)
    spouse_birth_place_country = Column(String, nullable=True)
    spouse_birth_place_city = Column(String, nullable=True)
    spouse_photo = Column(String, nullable=True)
    receipt_photo = Column(String, nullable=True)

    children = relationship(
        "Child", back_populates="user", cascade="all, delete, delete-orphan"
    )
    
    @property
    def has_spouse(self):
        return self.marital_status == "متاهل"
    
    @property
    def status_fa(self):
        return user_status_translations.get(self.status, "نامشخص")
    
    @property
    def is_finalized(self):
        return self.status == UserStatus.FINALIZED
    
    @property
    def icon(self):
        return "🙍🏻‍♀️" if self.gender == "خانم" else "🙍🏻‍♂️"

    @property
    def has_child(self):
        return self.children_count > 0

    @property
    def last_step(self):
        return 25 if self.has_spouse == True else 17

    @property
    def status_log(self):
        current_status_value = self.status
        steps_before = []
        steps_after = []
        current_status = None

        # Iterate through the UserStatus enum
        for status in UserStatus:
            if status.value < current_status_value:
                steps_before.append(user_status_translations[status])
            elif status.value == current_status_value:
                current_status = user_status_translations[status]
            # else:
            #     steps_after.append(user_status_translations[status])

        status_steps = []
        
        # Display the results
        for step in steps_before:
            status_steps.append(f"🟢 {step}")

        status_steps.append(f"🔵 {current_status}")
        
        for step in steps_after:
            status_steps.append(f"{step}")
        return "\n".join(status_steps)

    @property
    def is_awaiting_payment(self):
        return self.status == UserStatus.AWAINTING_PAYMENT.value
        

    @property
    def can_edit_info(self):
        return self.status < UserStatus.AWAINTING_PAYMENT.value
        

    @property
    def can_show_status_log(self):
        return self.status > UserStatus.COMPLETING.value
        
    @staticmethod
    def steps():
        return {
            1: {
                "field_name": "first_name",
                "title": "نام",
                "message": "نام (انگلیسی):",
                "type": "string",
                "example": "kambiz",
            },
            2: {
                "field_name": "last_name",
                "title": "نام خانوادگی",
                "message": "نام خانوادگی (انگلیسی):",
                "type": "string",
                "example": "barzegar",
            },
            3: {
                "field_name": "education_level",
                "title": "آخرین مدرک تحصیلی",
                "message": "آخرین مدرک تحصیلی:",
                "type": "dropdown",
                "choices": education_levels,
            },
            4: {
                "field_name": "gender",
                "title": "جنسیت",
                "message": "جنسیت:",
                "type": "dropdown",
                "choices": genders,
            },
            5: {
                "field_name": "birth_date",
                "title": "تاریخ تولد",
                "message": "تاریخ تولد:",
                "type": "string",
                "example": "۱ فروردین ۱۴۰۲",
            },
            6: {
                "field_name": "birth_place_country",
                "title": "کشور تولد",
                "message": "کشور تولد:",
                "type": "string",
                "example": "ایران",
            },
            7: {
                "field_name": "birth_place_city",
                "title": "شهر تولد",
                "message": "شهر تولد:",
                "type": "string",
                "example": "تهران",
            },
            8: {
                "field_name": "marital_status",
                "title": "وضعیت تاهل",
                "message": "وضعیت تاهل:",
                "type": "dropdown",
                "choices": marital_statuses,
            },
            9: {
                "field_name": "children_count",
                "title": "تعداد فرزند",
                "message": "تعداد فرزند:",
                "type": "string",
                "example": "۰ یا ۱ یا ۲ یا ۳",
            },
            10: {
                "field_name": "mobile_number",
                "title": "شماره همراه",
                "message": "شماره همراه:",
                "type": "string",
                "example": "09123456789",
            },
            11: {
                "field_name": "email",
                "title": "ایمیل",
                "message": "ایمیل:",
                "type": "string",
                "example": "hello@gmail.com",
            },
            12: {
                "field_name": "photo",
                "title": "عکس",
                "message": "عکس:",
                "type": "photo",
                "example": photo_example_captions,
            },
            13: {
                "field_name": "living_country",
                "title": "کشور محل زندگی",
                "message": "کشور محل زندگی:",
                "type": "string",
                "example": "ایران",
            },
            14: {
                "field_name": "living_province",
                "title": "استان محل زندگی",
                "message": "استان محل زندگی:",
                "type": "string",
                "example": "تهران",
            },
            15: {
                "field_name": "living_city",
                "title": "شهر محل زندگی",
                "message": "شهر محل زندگی:",
                "type": "string",
                "example": "تهران",
            },
            16: {
                "field_name": "living_postal_no",
                "title": "کد پستی",
                "message": "کد پستی:",
                "type": "string",
                "example": "1234567890 یا ندارم",
            },
            17: {
                "field_name": "living_address",
                "title": "آدرس",
                "message": "آدرس:",
                "type": "string",
                "example": "خیابان آزادی کوچه میمنت پلاک ۷ واحد ۳",
            },
            # همسر
            18: {
                "field_name": "spouse_first_name",
                "title": "نام همسر",
                "message": "نام همسر (انگلیسی):",
                "type": "string",
                "example": "kambiz",
            },
            19: {
                "field_name": "spouse_last_name",
                "title": "نام خانوادگی همسر",
                "message": "نام خانوادگی همسر (انگلیسی):",
                "type": "string",
                "example": "barzegar",
            },
            20: {
                "field_name": "spouse_education_level",
                "title": "آخرین مدرک تحصیلی همسر",
                "message": "آخرین مدرک تحصیلی همسر:",
                "type": "dropdown",
                "choices": education_levels,
            },
            21: {
                "field_name": "spouse_gender",
                "title": "جنسیت همسر",
                "message": "جنسیت همسر:",
                "type": "dropdown",
                "choices": genders,
            },
            22: {
                "field_name": "spouse_birth_date",
                "title": "تاریخ تولد همسر",
                "message": "تاریخ تولد همسر:",
                "type": "string",
                "example": "۱ فروردین ۱۴۰۲",
            },
            23: {
                "field_name": "spouse_photo",
                "title": "عکس همسر",
                "message": "عکس همسر:",
                "type": "photo",
                "example": photo_example_captions,
            },
            24: {
                "field_name": "spouse_birth_place_country",
                "title": "کشور تولد همسر",
                "message": "کشور تولد همسر:",
                "type": "string",
                "example": "ایران",
            },
            25: {
                "field_name": "spouse_birth_place_city",
                "title": "شهر تولد همسر",
                "message": "شهر تولد همسر:",
                "type": "string",
                "example": "تهران",
            },
        }
