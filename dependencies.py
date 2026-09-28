from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from security import decode_access_token

#SwaggerでAuthorizeが使える
security = HTTPBearer()

def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="認証に失敗しました"
        )

    return int(payload["sub"])