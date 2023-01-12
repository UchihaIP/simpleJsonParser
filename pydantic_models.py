from enum import Enum

import phonenumbers
from pydantic import BaseModel, EmailStr, Field
from pydantic.validators import strict_str_validator


class PhoneNumber(str):
    """Валидация номера телефона, с использованием телефонных номеров Google"""

    @classmethod
    def __get_validators__(cls):
        yield strict_str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        # Remove spaces
        v = v.strip().replace(' ', '')

        try:
            pn = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('invalid phone number format')
        result = cls(phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164))
        return result.lstrip("+")


class PhoneDetail(BaseModel):
    city: str
    country: str
    number: str


class ContactsInfo(BaseModel):
    email: EmailStr
    name: str = Field(..., alias="fullName")
    phone: PhoneNumber | PhoneDetail


class CoordinatesInfo(BaseModel):
    latitude: float
    longitude: float


class ExperienceInfo(BaseModel):
    id: str


class EmploymentEnum(str, Enum):
    fullDay = "fullDay"
    partTime = "partTime"
    remote = "remote"


class ScheduleInfo(BaseModel):
    id: EmploymentEnum


class CurrencyEnum(str, Enum):
    USD = "USD"
    RUR = "RUR"
    EUR = "EUR"
    NOK = "NOK"


class AddressInfo(BaseModel):
    region: str
    city: str
    street_type: str | None
    street: str | None
    house_type: str | None
    house: int | str | None
    value: str
    lat: float
    lng: float


class SalaryInfo(BaseModel):
    from_: int = Field(..., alias="from")
    to: int
    currency: CurrencyEnum
    gross: bool
