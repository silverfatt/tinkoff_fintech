from fastapi import HTTPException, status
from pydantic import BaseModel, validator


class User_s(BaseModel):
    login: str
    password: str

    @validator('login')
    def check_name(cls, value: str) -> str:
        if not value or value.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='NAME CANNOT BE EMPTY'
            )
        if len(value) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='NAME TOO LONG(>20)'
            )
        return value

    @validator('password')
    def check_password(cls, value: str) -> str:
        if not value or value.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='PASSWORD CANNOT BE EMPTY',
            )
        if len(value) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='PASSWORD IS TOO LONG(>30)',
            )
        return value

    def __repr__(self) -> str:
        return f'User {self.login}, password: {self.password}'


class Film_s(BaseModel):
    title: str
    date_of_release: int
    director: str

    @validator('title')
    def check_title(cls, value: str) -> str:
        if not value or value.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='TITLE CANNOT BE EMPTY'
            )
        if len(value) > 40:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='TITLE TOO LONG (>40)',
            )
        return value

    @validator('date_of_release')
    def check_date(cls, value: int) -> int:
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='DATE CANNOT BE EMPTY'
            )
        if value < 0 or value > 9999:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='DATE IS INCORRECT (MUST BE 0-9999)',
            )
        return value

    @validator('director')
    def check_director(cls, value: str) -> str:
        if not value or value.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='DIRECTOR CANNOT BE EMPTY',
            )
        if len(value) > 40:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DIRECTOR'S NAME TOO LONG(>40)",
            )
        return value
