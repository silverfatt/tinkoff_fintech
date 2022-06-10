from fastapi import HTTPException, status
from pydantic import BaseModel, validator


class UserScheme(BaseModel):
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


class TierScheme(BaseModel):
    tier: int

    @validator('tier')
    def check_number(cls, value: int) -> int:
        if 1 <= value <= 5:
            return value
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='INCORRECT BUILDING NUMBER',
        )


class Name(BaseModel):
    name: str

    @validator('name')
    def check_name(cls, name: str) -> str:
        if len(name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='NAME IS TOO LONG (>50)',
            )
        if len(name) == 0 or name.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='NAME CANNOT BE EMPTY',
            )
        return name


class Message(BaseModel):
    text: str

    @validator('text')
    def check_name(cls, text: str) -> str:
        if len(text) == 0 or text.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='MESSAGE CANNOT BE EMPTY',
            )
        return text


class Amount(BaseModel):
    amount: int

    @validator('amount')
    def check_name(cls, amount: int) -> int:
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='AMOUNT MUST BE A NATURAL NUMBER',
            )

        return amount
