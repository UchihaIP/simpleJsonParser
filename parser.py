import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from custom_exceptions import InfoAboutFileError
from pydantic_models import (EmploymentEnum,
                             AddressInfo,
                             SalaryInfo,
                             ContactsInfo,
                             CoordinatesInfo,
                             ExperienceInfo,
                             PhoneDetail,
                             ScheduleInfo)


class NewJsonBody(BaseModel):
    """Модель для валидации конвертированной json структуры."""
    address: str
    allow_messages: bool
    billing_type: Literal["packageOrSingle"] | str
    business_area: int
    contacts: ContactsInfo
    coordinates: CoordinatesInfo
    description: str
    experience: ExperienceInfo
    html_tags: bool
    image_url: HttpUrl
    name: str
    salary: int
    salary_range: SalaryInfo = Field(..., exclude={"currency", "gross"})
    schedule: ScheduleInfo


class OldJsonBody(BaseModel):
    """Модель для валидации входного json объекта."""
    description: str
    employment: EmploymentEnum
    address: AddressInfo
    name: str
    salary: SalaryInfo
    contacts: ContactsInfo


class JsonConverter:

    def start_converting(self) -> None:
        """Запуск создания процесса конвертации json объекта."""
        _parsed_data: OldJsonBody = self._get_raw_json()
        result_dct: dict[NewJsonBody] = self._converting_json_structure(_parsed_data)
        self._export_to_json(result_dct)

    def _converting_json_structure(self, parsed_data: OldJsonBody) -> dict[NewJsonBody]:
        """Процесс преобразования json структуры."""
        _phone_number = parsed_data.contacts.phone
        result: NewJsonBody = NewJsonBody(address=parsed_data.address.value,
                                          allow_messages=True,
                                          billing_type="packageOrSingle",
                                          business_area=1,
                                          contacts=ContactsInfo(
                                              email=parsed_data.contacts.email,
                                              fullName=parsed_data.contacts.name,
                                              phone=PhoneDetail(
                                                  city=_phone_number[1:4],
                                                  country=_phone_number[0],
                                                  number="{}-{}-{}".format(_phone_number[4:7],
                                                                           _phone_number[7:9],
                                                                           _phone_number[9:])
                                              )
                                          ),
                                          coordinates=CoordinatesInfo(
                                              latitude=parsed_data.address.lat,
                                              longitude=parsed_data.address.lng
                                          ),
                                          description=parsed_data.description,
                                          experience=ExperienceInfo(
                                              id="noMatter"
                                          ),
                                          html_tags=self.__check_html_tags_in_description(parsed_data),
                                          image_url="https://img.hhcdn.ru/employer-logo/3410666.jpeg",
                                          name=parsed_data.name,
                                          salary=70000,
                                          salary_range=parsed_data.salary,
                                          schedule=ScheduleInfo(
                                              id=parsed_data.employment
                                          )
                                          )

        return result.dict(by_alias=True)

    @staticmethod
    def _get_raw_json() -> OldJsonBody:
        """Получаем json объект из файла."""
        path = Path("raw_data.json")
        parse_data: OldJsonBody = OldJsonBody.parse_file(path)
        return parse_data

    @staticmethod
    def _export_to_json(data: dict[NewJsonBody]) -> None:
        """Запись преобразованного json объекта в файл."""
        with open("result_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def __check_html_tags_in_description(data: OldJsonBody) -> bool:
        """Проверяем есть ли html теги в поле 'description'.
        Если они присутствуют, то в новом json объекте в поле 'html_tags',
        ставится 'True'.
        """
        presence_of_tags = False
        if ("<ul>" or "<li>") in data.description:
            presence_of_tags = True
        return presence_of_tags

    @staticmethod
    def show_new_json() -> dict[NewJsonBody]:
        try:
            with open("result_data.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as e:
            raise InfoAboutFileError("Файл ещё не создан, запустите функцию start_converting().")


ctr = JsonConverter()
ctr.start_converting()
