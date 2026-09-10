from db import get_connection

class UserManager:
    def create_user(self, username, password_hash):
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users(username, password_hash)
                    VALUES (%s, %s)
                    """,
                    (username, password_hash)
                )
                connection.commit()
    
    def get_user_by_username(self, username):
        with get_connection() as connection:
           with connection.cursor() as cursor:            
                cursor.execute(
                """
                SELECT id, username, password_hash 
                FROM users
                WHERE username = %s
                """,
                (username,)
                )        
                user = cursor.fetchone()
        
        return user