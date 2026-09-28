from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from user_manager import UserManager
from security import hash_password, verify_password, create_access_token
from psycopg2.errors import UniqueViolation

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

manager = UserManager()

class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("ユーザー名を入力してください")
        
        return value
    
class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register_user(user: UserCreate):
    password_hash = hash_password(user.password)
    try:
        manager.create_user(
            user.username,
            password_hash
        )
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="そのユーザー名は既に使用されています"
        )
    
    return {"message": "ユーザー登録が完了しました"}

@router.post("/login")
def login(user: UserLogin):
    db_user = manager.get_user_by_username(user.username)
    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="ユーザー名またはパスワードが間違っています"
        )

    if not verify_password(user.password, db_user[2]):
        raise HTTPException(
            status_code=401,
            detail="ユーザー名またはパスワードが間違っています"
        )

    access_token = create_access_token(db_user[0])

    return {
       "access_token": access_token,
       "token_type": "bearer"
    }