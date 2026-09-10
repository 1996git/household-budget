from datetime import date
from fastapi import APIRouter, Query, status, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from expense_manager import ExpenseManager
from dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])

manager = ExpenseManager()

class ExpenseResponse(BaseModel):
    id: int
    category: str
    amount: int
    expense_date: date

class ExpenseCreate(BaseModel):
    category: str = Field(min_length=1)
    amount: int = Field(gt=0)
    expense_date: date

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("カテゴリーを入力してください")

        return value
    
class ExpenseUpdate(BaseModel):
    category: str = Field(min_length=1)
    amount: int = Field(gt=0)
    expense_date: date

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        value = value.strip()
        if not value:
           raise ValueError("カテゴリーを入力してください")
   
        return value

@router.get("/")
def get_expenses(user_id: int = Depends(get_current_user)):
    expenses = manager.get_expenses(user_id)
    #ExpenseResponseを書いてるのはget処理が一連の順序を経て起動する役割だから。
    return [ExpenseResponse(
            id=expense[0],
            category=expense[1], 
            amount=expense[2], 
            expense_date=expense[3]
         ) 
          for expense in expenses
        ]


@router.get("/search", response_model=list[ExpenseResponse])
def search_expenses(category: str = Query(...,), user_id: int = Depends(get_current_user)):
    expenses = manager.get_expenses_category(category, user_id)
    return [
        ExpenseResponse(
            id=expense[0], 
            category=expense[1],
            amount=expense[2], 
            expense_date=expense[3]
            ) 
        for expense in expenses
    ]

@router.get("/month")
def monthly_summary(year:int, month:int, user_id: int = Depends(get_current_user)):
    month_expenses = manager.monthly_summary(year, month, user_id)
    return month_expenses 

@router.get("/summary/category")
def category_summary(user_id: int = Depends(get_current_user)):
    return manager.category_summary(user_id)

@router.get("/summary/total")
def total_expense(user_id: int = Depends(get_current_user)):
    total = manager.total_expense(user_id)
    return {"total":total}

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, user_id = Depends(get_current_user)):
    expense = manager.get_expense(expense_id, user_id)
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="指定された支出が見つかりません"
        )
    return ExpenseResponse(
        id=expense[0],
        category=expense[1],
        amount=expense[2],
        expense_date=expense[3]
    )

"""
201の概要
・新しいデータが作成
・postの成功時に使う
・作成したデータを返すことも多い。
"""
#postはデータを新しく作る（登録）するメソッド
@router.post("/", status_code=201)
#関数を渡す際に型テェックをする必要が在る。
def create_expense(expense: ExpenseCreate, user_id: int = Depends(get_current_user)):
    manager.add_expense(
        expense.category,
        expense.amount,
        expense.expense_date,
        user_id
    )

    return {"message": "支出を追加しました"}

#putは既存データの更新
@router.put("/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseUpdate, user_id: int = Depends(get_current_user)):
    update_count = manager.update_expense(
        expense_id,
        expense.category,
        expense.amount,
        expense.expense_date,
        user_id
    )
    if update_count == 0:
        raise HTTPException(
            status_code=404,
            detail="指定された支出が見つかりません"
        )
    
    return {"message": "支出を更新しました"}

"""
204の概要
・処理は成功しているが、返すデータは存在しない。
・Deleteの成功時に使うのが標準
・returnを書いてはいけない
"""
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, user_id: int = Depends(get_current_user)):
    deleted_count = manager.del_expense(expense_id, user_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="指定された支出が見つかりません"
        )
