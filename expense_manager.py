from db import get_connection

class ExpenseManager:
    def add_expense(self, category, amount, date, user_id):
        with get_connection() as connection: #connectionはDBとの通信線
           with connection.cursor() as cursor: #通信線を使ってSQLを投げる
                cursor.execute(
                """
                INSERT INTO expenses(category, amount, expense_date, user_id)
                VALUES(%s, %s, %s, %s)
                RETURNING id
                """,
                (category, amount, date, user_id)
            )

                expense_id = cursor.fetchone()[0]

        return expense_id
        
    def get_expenses(self, user_id):
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM expenses
                WHERE user_id = %s
                ORDER BY id
                """,
                (user_id,)
                )

                rows = cursor.fetchall()
                    
        return rows

    def get_expense(self, expense_id, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM expenses
                    WHERE id = %s
                    AND user_id = %s
                    """,
                    (expense_id, user_id)
                )

                expense = cursor.fetchone()
        
         return expense

    def del_expense(self, expense_id, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
            cursor.execute(
            """
            DELETE FROM expenses
            WHERE id = %s
            AND user_id = %s
            """,
            (expense_id, user_id)
            )

            deleted_count = cursor.rowcount

         return deleted_count

    def update_expense(self, expense_id, category, amount, date, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE expenses
                SET category = %s,
                    amount = %s,
                    expense_date = %s
                WHERE id = %s
                AND user_id = %s
                """,
                (category, amount, date, expense_id, user_id)
            )

            update_count = cursor.rowcount

         return update_count

    def get_expenses_category(self, category, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM expenses
                    WHERE category = %s
                    AND user_id = %s
                    """,
                    (category, user_id)
                )

                rows = cursor.fetchall()

         return rows
     
    #グループ別に分けた全カテゴリー集計
    def category_summary(self, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT category, SUM(amount)
                FROM expenses
                WHERE user_id = %s
                GROUP BY category
                """,
                (user_id,)
            )
                rows = cursor.fetchall()
    
         return rows

    #全カテゴリー
    def total_expense(self,user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount),0)  
                FROM expenses
                WHERE user_id = %s
                """,
                (user_id,)
            )
            result = cursor.fetchone()
        
         return result[0]

    def monthly_summary(self, year, month, user_id):
         with get_connection() as connection:
           with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(amount),0)
                    FROM expenses
                    WHERE EXTRACT(YEAR FROM expense_date) = %s 
                    AND EXTRACT(MONTH FROM expense_date) = %s
                    AND user_id = %s
                    """,
                    (year, month, user_id)
                )
                result = cursor.fetchone()
                
         return result[0] 

