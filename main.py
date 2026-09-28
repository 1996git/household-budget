from fastapi import FastAPI
from routers.expenses import router as expenses_router
from routers.users import router as users_router

app = FastAPI()

app.include_router(expenses_router)
app.include_router(users_router)

#getはデータを取得するためのメソッド
@app.get("/")
def home():
    return {"message":"Expense API is running"}
