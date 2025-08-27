import pymssql
import logging
from helpers import send_email

class AuthService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def request_login_code(self, email: str):
        try:
            with self.db.cursor() as cursor:
                sql = "DECLARE @code_out NCHAR(6); EXEC usp_generate_login_code @email=%s, @plainTextCode=@code_out OUTPUT; SELECT @code_out;"
                cursor.execute(sql, (email,))
                result = cursor.fetchone()

                if result and result[0]:
                    plain_text_code = result[0]
                    
                    email_subject = "Your One-Time Login Code"
                    email_body = f"""
                    <html><body>
                        <p>Hello,</p>
                        <p>Your one-time login code is: <strong>{plain_text_code}</strong></p>
                        <p>This code will expire in 60 minutes.</p>
                        <p>If you did not request this code, you can safely ignore this email.</p>
                        <p>Thank you,<br>BU Reporting Team</p>
                    </body></html>
                    """
                    
                    email_sent = send_email(to_email=email, subject=email_subject, html_content=email_body)
                    
                    if not email_sent:
                        raise Exception("Failed to send the login code email.")
                    
                    self.db.commit()
            
        except pymssql.Error as ex:
            logging.error(f"Database Service Error in request_login_code: {ex}")
            raise
        except Exception as e:
            logging.error(f"Service layer error in request_login_code: {e}")
            raise
                
        return {"message": "A login code has been sent to your email. Please check your inbox."}

    def verify_login_and_get_user(self, email: str, code: str):
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_verify_login_code', (email, code))
                user_data = cursor.fetchone()
                
                if user_data and user_data.get('user_id') > 0:
                    user_id = user_data['user_id']
                    first_name = user_data.get('first_name', 'User')
                    is_admin = user_data.get('is_admin', False)

                    cursor.callproc('usp_get_user_permissions', (user_id,))
                    permissions = cursor.fetchall()

                    self.db.commit()

                    return {
                        "user_id": user_id,
                        "is_admin": is_admin,
                        "status": "success",
                        "message": f"Welcome, {first_name}!",
                        "permissions": permissions
                    }
                else:
                    return {"user_id": 0, "status": "failed", "message": "Invalid or expired login code."}
        except pymssql.Error as ex:
            logging.error(f"Database Service Error in verify_login_and_get_user: {ex}")
            print(f"Database Service Error in verify_login_and_get_user: {ex}")
            raise