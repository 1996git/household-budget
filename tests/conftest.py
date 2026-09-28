import pytest
from db import get_connection
from security import hash_password
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#==========
#認証
#==========

@pytest.fixture
def auth_headers(test_user):
    response = client.post(
        "/users/login",
        json={
            "username":test_user["username"],
            "password":test_user["password"]
        }
    )

    token = response.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}"
    }


#==========
#テストユーザー
#==========

#事前にDBにユーザーを作る
@pytest.fixture
def test_user():
    username = "login_test_user"
    password = "password123"

    password_hash = hash_password(password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                    """
                    INSERT INTO users(username, password_hash)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (username, password_hash)
                )
            
            user_id = cursor.fetchone()[0]
    try:
        yield {
            "id": user_id,
            "username": username,
            "password": password
        }
    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM expenses
                    WHERE user_id = %s
                    """,
                    (user_id,)
            )
                cursor.execute(
                    """
                    DELETE FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
            )

@pytest.fixture
def other_user():
    username = "other_test_user"
    password = "password123"

    password_hash = hash_password(password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users(username, password_hash)
                VALUES(%s, %s)
                RETURNING id
                """,
                (username, password_hash)
            )

            user_id = cursor.fetchone()[0]
    yield {
        "id": user_id,
        "username": username,
        "password": password
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM users
                WHERE id = %s
                """,
                (user_id,)
            )



#==========
#テスト用支出
#==========

@pytest.fixture
def test_expense(test_user):
     with get_connection() as connection:
        with connection.cursor() as cursor:
           cursor.execute(
              """
                INSERT INTO expenses(category, amount, expense_date, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
              """,
                    ("テスト", 999, "2026-09-11", test_user["id"])
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

@pytest.fixture
def other_user_expense(other_user):
     with get_connection() as connection:
        with connection.cursor() as cursor:
           cursor.execute(
              """
                INSERT INTO expenses(category, amount, expense_date, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
              """,
                    ("他ユーザー", 3000, "2026-09-14", other_user["id"])
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


#==========
#ユーザー登録テスト
#==========

@pytest.fixture
def register_test_user():
    username = "register_test_user"
    password = "password123"

    yield{
        "username":username,
        "password":password
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM users
                WHERE username = %s
                """,
                (username,)
            )

@pytest.fixture
def hash_test_user():
    username =  "hash_test_user"
    password = "password123"

    yield{
        "username":username,
        "password":password
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM users
                WHERE username = %s
                """,
                (username,)
            )
            