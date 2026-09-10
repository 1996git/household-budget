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

def main():
    while True:
        print("\n家計簿")
        print("1. 支出追加")
        print("2. 支出一覧")
        print("3. 支出削除")
        print("4. 支出更新")
        print("5. 合計金額")
        print("6. カテゴリー別集計")
        print("7. 支出検索")
        print("8. 月別集計")
        print("9. 収入追加")
        print("10. 残額確認")
        print("11. CSV保存")
        print("12. 終了")

        choice = input("選択してください: ")

        if choice == '1':
            category = input("カテゴリーを入力してください")
            amount = int(input("金額を入力してください"))
            expense_date = date.today()
            manager.add_expense(category, amount, expense_date)

        elif choice == '2':
            expenses = manager.get_expenses()
            if not expenses:
                print("支出はまだ登録されていません")
            else:
                for id, category, amount, expense_date in expenses:
                    print(f"{id}|{category}|{amount}|{expense_date:%Y-%m-%d}")

        elif choice == '3':
            expenses= manager.get_expenses()
            try:
                index = int(input("削除する番号：")) - 1
                expense_id = expenses[index][0]
            except (ValueError, IndexError):
                print("正しい番号を入力してください") 
            else:   
                manager.del_expense(expense_id)
                print("削除しました")

        elif choice == '4':
            expense_id = int(input("変更する支出ID: "))
            category = input("新しいカテゴリー: ")
            amount = int(input("新しい金額: "))
            new_date = input("新しい日付: ")
            manager.update_expense(
                expense_id,
                category,
                amount,
                new_date
            )
            print("支出を変更しました")            

        elif choice == '5':
            total = manager.total_expense()
            print(f"合計金額:{total}円")

        elif choice == '6':
            categories = manager.get_categories()
            for index, category in enumerate(categories, start=1):
                print(f"{index}. {category[0]}")
            try:
               category_index = int(input("カテゴリー番号を選択してください：")) - 1
               category = categories[category_index][0]
            except (ValueError,IndexError):
                print("範囲内の数値を入力してください。")
            else:
                expenses = manager.get_expenses_category(category)
                for id, category, amount, expense_date in expenses:
                    print(f"{id} | {category} | {amount} | {expense_date}")

                total = manager.get_category_total(category)
                print(f"{category}の合計金額は{total}円です。")

                group_category = manager.category_summary()
                for category, sum in group_category:
                    print(f"{category}:{sum}円")

        elif choice == '7':
             keyword = input("検索するカテゴリーを入力してください")
             results = manager.search_expenses(keyword)
             if not results:
                print("該当する支出はありません")   
             else:
                for result_list in results:
                    print(f"{result_list.date} / {result_list.category} / {result_list.amount}円")

        elif choice == '8':
            month = input("集計する年月を入力してください")
            month_total = manager.total_month(month)
            print(f"{month}の支出合計:{month_total}円")

        elif choice == '9':
            try:
               amount = int(input("金額を入力してください："))
            except ValueError:
               print("数値で入力してください")
            else:
               manager.add_income(amount)

        elif choice == '10':
             balance = manager.total_amount()
             print(f"残高：{balance}円")

        elif choice == '11':
             manager.save_csv("expenses.csv")
             print("保存しました")
             break
        
        elif choice == '12':
             print("終了します")
             break
        
        else:
             print("1~12の範囲で入力してください")

if __name__ == "__main__":
     main()