from fastapi.testclient import TestClient
from main import app
from security import verify_password
from db import get_connection
from datetime import datetime, timedelta, timezone 
import jwt
from security import SECRET_KEY, ALGORITHM

client = TestClient(app)

def test_get_expense_not_found(auth_headers):
    response = client.get(
        "/expenses/999999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_get_other_user_expense(auth_headers, test_expense, other_user_expense):
     response = client.get(
          f"/expenses/{other_user_expense}",
          headers=auth_headers
     )

     assert response.status_code == 404


def test_get_expenses_response(auth_headers):
     response = client.get(
        "/expenses/",
        headers=auth_headers
    )
    
     assert response.status_code == 200

     data = response.json()
     assert isinstance(data, list)
     for expense in data:
         assert "id" in expense
         assert "category" in expense
         assert "amount" in expense
         assert "expense_date" in expense


def test_get_expenses_only_own_data(auth_headers, test_expense):
        response = client.get(
            "/expenses/",
             headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        ids = [expense["id"] for expense in data]
        assert test_expense in ids


def test_create_expense(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"テスト登録",
               "amount": 1500,
               "expense_date": "2026-09-14"
          }
     )

     assert response.status_code == 201
     data = response.json()
     assert "id" in data
     assert data["category"] == "テスト登録"
     assert data["amount"] == 1500
     assert data["expense_date"] == "2026-09-14"


def test_create_expense_invalid_amount(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"テスト",
               "amount": 0,
               "expense_date": "2026-09-14"
          }
     )

     assert response.status_code == 422


def test_create_expense_negative_amount(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"テスト",
               "amount":-100,
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


def test_create_expense_invalid_amount_type(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"テスト",
               "amount":"abc",
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


def test_create_expense_invalid_date(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"テスト",
               "amount":1000,
               "expense_date":"invalid_date"
          }
     )

     assert response.status_code == 422


def test_create_expense_empty_category(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":"",
               "amount":1000,
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


def test_create_expense_whitespace_category(auth_headers):
     response = client.post(
          "/expenses/",
          headers=auth_headers,
          json={
               "category":" ",
               "amount":1000,
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


#putは特定の１件を更新するためURLにidを指定する必要がある。
def test_update_expense(auth_headers, test_expense):
    response = client.put(
        f"/expenses/{test_expense}",
        headers=auth_headers,
        json={
            "category": "更新テスト",
            "amount": 2000,
            "expense_date": "2026-09-14"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "支出を更新しました"


def test_update_other_user_expense(auth_headers, other_user_expense):
    response = client.put(
        f"/expenses/{other_user_expense}",
        headers=auth_headers,
        json={
            "category": "不正な更新",
            "amount": 99999,
            "expense_date": "2026-09-14"
        }
    )

    assert response.status_code == 404


def test_update_expense_invalid_amount(auth_headers, test_expense):
     response = client.put(
          f"/expenses/{test_expense}",
          headers=auth_headers,
          json={
               "category":"更新テスト",
               "amount":0,
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


def test_update_expense_invalid_category(auth_headers, test_expense):
     response = client.put(
          f"/expenses/{test_expense}",
          headers=auth_headers,
          json={
               "category":"",
               "amount":1000,
               "expense_date":"2026-09-14"
          }
     )

     assert response.status_code == 422


def test_update_expense_invalid_date(auth_headers, test_expense):
     response = client.put(
          f"/expenses/{test_expense}",
          headers=auth_headers,
          json={
               "category":"更新テスト",
               "amount":1000,
               "expense_date":""
          }
     )

     assert response.status_code == 422


def test_delete_other_user_expense(auth_headers, other_user_expense):
     response = client.delete(
          f"/expenses/{other_user_expense}",
          headers=auth_headers
     )

     assert response.status_code == 404


def test_delete_expense(auth_headers, test_expense):
     response = client.delete(
          f"/expenses/{test_expense}",
          headers=auth_headers
     )

     assert response.status_code == 204


def test_delete_expense_not_found(auth_headers):
    response = client.delete(
         "/expenses/999999",
         headers=auth_headers
    )

    assert response.status_code == 404


def test_get_expenses_without_auth():
     response = client.get("/expenses/")

     assert response.status_code == 401


def test_get_expenses_with_invalid_token():
     response = client.get(
          "/expenses",
          headers={
               "Authorization": "Bearer invalid_token"
          }
     )

     assert response.status_code == 401


def test_get_expenses_with_expired_token(test_user):
    expired_token = jwt.encode(
        {
            "sub": test_user["id"],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/expenses/",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401


#新規ユーザーを登録
def test_register_user(register_test_user):
     response = client.post(
          "/users/register",
          json={
               "username":register_test_user["username"],
               "password":register_test_user["password"]
          }
     )

     assert response.status_code == 201
     assert response.json()["message"] == "ユーザー登録が完了しました"


def test_register_user_password_is_hashed(hash_test_user):
     response = client.post(
          "/users/register",
          json={
               "username":hash_test_user["username"],
               "password":hash_test_user["password"]
          }
     )

     assert response.status_code == 201

     with get_connection() as connection:
        with connection.cursor() as cursor:
             cursor.execute(
                  """
                  SELECT password_hash 
                  FROM users
                  WHERE username = %s
                  """,
                  (hash_test_user["username"],)
             )

             result = cursor.fetchone()

     assert result is not None
     password_hash = result[0]

     assert password_hash != hash_test_user["password"]
     assert verify_password(hash_test_user["password"], password_hash)


def test_register_user_without_password():
     response = client.post(
          "/users/register",
          json={
               "username":"validation_test_user"
          }
     )

     assert response.status_code == 422


def test_register_user_without_username():
     response = client.post(
           "/users/register",
          json = {
               "password":"validation_test_password"
          }
     )

     assert response.status_code == 422


def test_register_user_empty_username():
    for username in ["", " "]:
        response = client.post(
           "/users/register",
           json={
               "username":username,
               "password":"password123"
          }
     )

        assert response.status_code == 422


def test_register_user_username_strip():
     response = client.post(
          "/users/register",
          json={
               "username":" test_strip_user_001 ",
               "password":"password123"
          }
     )

     assert response.status_code == 201

     with get_connection() as connection:
          with connection.cursor() as cursor:
               cursor.execute(
                    """
                    SELECT username
                    FROM users
                    WHERE username = %s
                    """,
                    ("test_strip_user_001",)
               )

               result = cursor.fetchone()

     assert result[0] == "test_strip_user_001"


def test_register_user_with_short_password():
     response = client.post(
          "/users/register",
          json={
               "username":"short_password_user",
               "password":"1234567"
          }
     )

     assert response.status_code == 422


def test_register_user_with_short_username():
     response = client.post(
          "/users/register",
          json={
               "username":"ab",
               "password":"password123"
          }
     )

     assert response.status_code == 422


#同じユーザー名で登録
def test_register_duplicate_username(test_user):
     response = client.post(
          "/users/register",
          json={
               "username":test_user["username"],
               "password":"password123"
          }
     )

     assert response.status_code == 409
     assert response.json()["detail"] == ("そのユーザー名は既に使用されています")



#既存ユーザーでログイン           
def test_login(test_user):
     response = client.post(
          "/users/login",
          json={
               "username":test_user["username"],
               "password":test_user["password"]
          }
     )

     assert response.status_code == 200

     data = response.json()

     assert "access_token" in data
     assert data["token_type"] == "bearer"


def test_login_with_invalid_username():
     response = client.post(
          "/users/login",
          json={
               "username":"not_exist_user",
               "password":"password123"
          }
     )

     assert response.status_code == 401
     assert response.json()["detail"] == ("ユーザー名またはパスワードが間違っています")


def test_login_with_wrong_password(test_user):
     response = client.post(
          "/users/login",
          json={
               "username":test_user["username"],
               "password":"wrong_password"
          }
     )

     assert response.status_code == 401
     assert response.json()["detail"] == ("ユーザー名またはパスワードが間違っています")


def test_login_without_password(test_user):
     response = client.post(
          "/users/login",
          json={
               "username":test_user["username"]
          }
     )

     assert response.status_code == 422


def test_login_without_username(test_user):
     response = client.post(
          "/users/login",
          json={
               "password":test_user["password"]
          }
     )

     assert response.status_code == 422


def test_search_expenses(auth_headers, test_expense):
     response = client.get(
          "/expenses/search/",
          headers=auth_headers,
          params={
               "category":"テスト"
          }
     )

     assert response.status_code == 200
     data = response.json()
     assert isinstance(data, list)
     ids = [expense["id"] for expense in data]
     assert test_expense in ids


def test_search_expenses_only_own_data(auth_headers, test_expense, other_user_expense):
     response = client.get(
          "/expenses/search",
          headers=auth_headers,
          params={
               "category":"テスト"
          }
     )

     assert response.status_code == 200
     data = response.json()
     ids = [expense["id"] for expense in data]
     assert test_expense in ids
     assert other_user_expense not in ids


def test_monthly_summary(auth_headers, test_expense):
     response = client.get(
          "/expenses/month",
          headers=auth_headers,
          params={
             "year":2026,
             "month":9
          }
     )

     assert response.status_code == 200
     data = response.json()
     assert data["year"] == 2026
     assert data["month"] == 9
     assert data["total"] == 999


def test_monthly_summary_invalid_month(auth_headers):
    for month in [0, 13]:
          response = client.get(
               "/expenses/month",
               headers=auth_headers,
               params={
                    "year":2026,
                    "month":month
               }
          )
          assert response.status_code == 422


def test_monthly_summary_no_expenses(auth_headers):
     response = client.get(
          "/expenses/month",
          headers=auth_headers,
          params={
               "year":2026,
               "month":9
          }
     )

     assert response.status_code == 200
     data = response.json()
     assert data["year"] == 2026
     assert data["month"] == 9
     assert data["total"] == 0

def test_monthly_summary_only_own_data(auth_headers, test_expense, other_user_expense):
     response = client.get(
          "/expenses/month",
          headers=auth_headers,
          params={
               "year":2026,
               "month":9
          }
     )

     assert response.status_code == 200
     data = response.json()
     assert data["year"] == 2026
     assert data["month"] == 9
     assert data["total"] == 999


def test_category_summary(auth_headers, test_expense):
     response = client.get(
          "/expenses/summary/category",
          headers=auth_headers
     )

     assert response.status_code == 200
     data = response.json()
     assert {"category":"テスト", "total":999} in data


def test_category_summary_only_own_data(auth_headers, test_expense, other_user_expense):
     response = client.get(
          "/expenses/summary/category",
          headers=auth_headers
     )

     assert response.status_code == 200
     data = response.json()
     assert {"category":"テスト", "total":999} in data
     assert {"catetory":"他ユーザー", "total":3000} not in data


def test_total_expense(auth_headers, test_expense):
     response = client.get(
          "expenses/summary/total",
          headers=auth_headers     
     )

     assert response.status_code == 200
     data = response.json()
     assert data["total"] == 999


def test_total_expense_only_data(auth_headers, test_expense, other_user_expense):
    response = client.get(
         "/expenses/summary/total",
         headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 999


def test_total_expense_no_expenses(auth_headers):
     response = client.get(
          "/expenses/summary/total",
          headers=auth_headers,
     )
     assert response.status_code == 200
     data = response.json()
     assert data["total"] == 0