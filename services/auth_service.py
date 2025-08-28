import pymssql
import logging
import re
from helpers import send_email
from exceptions import InvalidCredentialsError


class AuthService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def request_login_code(self, email: str):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email provided.")
        
        try:
            with self.db.cursor() as cursor:
                cursor.callproc('usp_generate_login_code', (email,))
                result = cursor.fetchone()

                if result and result.get('login_code'):
                    login_code = result['login_code']
                    
                    email_subject = "Your One-Time Login Code"
                    email_body = f"""
                    <html><body>
                        <p>Hello,</p>
                        <p>Your one-time login code is: <strong>{login_code}</strong></p>
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

                    cursor.callproc('usp_get_user_permissions', (user_id,))
                    permissions = cursor.fetchall()

                    self.db.commit()

                    user_session_data = {
                        "is_admin": user_data.get('is_admin', False),
                        "period_start": user_data.get('period_start'),
                        "period_end": user_data.get('period_end'),
                        "is_period_closed": user_data.get('is_period_closed', False),
                        "is_priorities_month": user_data.get('is_priorities_month', False),
                        "permissions": permissions
                    }

                    return {
                        "user_id": user_id,
                        "status": "success",
                        "message": f"Welcome, {first_name}!",
                        "data": user_session_data
                    }
                else:
                    raise InvalidCredentialsError()
        except pymssql.Error as ex:
            logging.error(f"Database Service Error in verify_login_and_get_user: {ex}")
            raise