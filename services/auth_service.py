import pymssql
import re


from helpers import send_email
from config import logger
from exceptions import EmailNotFoundError, InvalidLoginCodeError


class AuthService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def request_login_code(self, email: str) -> dict:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            logger.warning(f"Invalid email format attempted: {email}")
            raise ValueError("Invalid email format provided.")

        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_generate_login_code', (email,))
                result = cursor.fetchone()

                if result.get('login_code') is None:
                    logger.warning(f"Email not found in database: {email}")
                    raise EmailNotFoundError("Email not found.")

                if not result.get('login_code'):
                    logger.error(f"No login code generated for email: {email}")
                    raise Exception("Failed to generate login code.")

                login_code = result['login_code']
                email_subject = "Your One-Time Login Code"
                email_body = f"""
                <html><body>
                    <p>Hello,</p>
                    <p>Your one-time login code is: <strong>{login_code}</strong></p>
                    <p>This code will expire in <strong>60 minutes</strong>.</p>
                    <p>If you did not request this code, you can safely ignore this email.</p>
                    <br>
                    <p>Thank you,<br><em>BU Reporting Team</em></p>
                </body></html>
                """

                email_sent = send_email(to_email=email, subject=email_subject, html_content=email_body)
                if not email_sent:
                    logger.error(f"Failed to send login code email to: {email}")
                    raise Exception("Failed to send the login code email.")

                self.db.commit()
                logger.info(f"Login code sent and committed for email: {email}")

        except pymssql.Error as ex:
            logger.error(f"Database Service Error in request_login_code: {ex}")
            raise
        except Exception as e:
            logger.error(f"Service layer error in request_login_code: {e}")
            raise

        return {"message": "A login code has been sent to your email. Please check your inbox."}


    def verify_login_and_get_user(self, email: str, code: str) -> dict:
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_verify_login_code', (email, code))
                user_data = cursor.fetchone()

                if not user_data:
                    logger.warning(f"Email not found in database during login attempt: {email}")
                    raise EmailNotFoundError("Email not found.")

                if user_data.get('user_id', 0) <= 0:
                    logger.warning(f"Invalid or expired login code for email: {email}")
                    raise InvalidLoginCodeError("Invalid or expired login code.")

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

                logger.info(f"User {user_id} ({email}) successfully logged in.")
                return {
                    "user_id": user_id,
                    "status": "success",
                    "message": f"Welcome, {first_name}!",
                    "data": user_session_data
                }
        except pymssql.Error as ex:
            logger.error(f"Database Service Error in verify_login_and_get_user: {ex}")
            raise
        except Exception as e:
            logger.error(f"Service layer error in verify_login_and_get_user: {e}")
            raise