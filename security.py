from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt 
from dotenv import load_dotenv
import os

#envを読み込む
load_dotenv()

#SECRET_KEYとALGORITHMを環境変数から取得
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

password_hash = PasswordHash.recommended()

#passwordをハッシュ化
def hash_password(password):
    return password_hash.hash(password)

#ハッシュ化されたpasswordを検証
def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    #payloadをJWTトークンに変換して返す
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        return None
    
    except jwt.InvalidTokenError:
        return None
    