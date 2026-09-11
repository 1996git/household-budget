import pytest
from security import create_access_token
from db import get_connection

@pytest.fixture
def auth_headers():
    token = create_access_token(1)

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def test_expense():
     with get_connection() as connection:
        with connection.cursor() as cursor:
           cursor.execute(
              """
                INSERT INTO expenses(category, amount, expense_date, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
              """,
                    ("テスト", 999, "2026-09-11", 1)
                )
           expense_id = cursor.fetchone()[0]

     yield expense_id

     with get_connection() as connection:
       with connection.cursor() as cursor:
            cursor.execute(
               """
               DELETE FROM expenses
               WHERE id = %s
               """,
               (expense_id,)
           )