from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from user_manager import UserManager
from security import hash_password, verify_password, create_access_token

router = APIRouter(
    tags=["users"]
)

manager = UserManager()

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register_user(user: UserCreate):
    password_hash = hash_password(user.password)
    manager.create_user(
        user.username,
        password_hash
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