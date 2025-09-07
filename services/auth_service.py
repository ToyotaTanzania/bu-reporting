import pymssql
import re
from typing import Dict, Any
from helpers import send_email
from config import logger
from exceptions import EmailNotFoundError, InvalidLoginCodeError, UserNotActiveError

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
LOGIN_CODE_EXPIRY_MINUTES = 60

class AuthService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def request_login_code(self, email: str) -> Dict[str, str]:
        if not re.match(EMAIL_REGEX, email):
            logger.warning(f"Invalid email format attempted: {email}")
            raise ValueError("Invalid email format provided.")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_generate_login_code', (email,))
                result = cursor.fetchone()

                if not result or not result.get('email_exists', False):
                    logger.warning(f"Email not found: {email}")
                    raise EmailNotFoundError("Email not found.")
                
                if not result.get('is_active', False):
                    logger.warning(f"User is not active: {email}")
                    raise UserNotActiveError("User is not active.")
                
                login_code = result.get('login_code')
                minutes_to_expire = result.get('minutes_to_expire', LOGIN_CODE_EXPIRY_MINUTES)

                if not login_code:
                    logger.error(f"No login code generated for email: {email}")
                    raise Exception("Failed to generate login code.")
                
                email_subject = "Your One-Time Login Code"
                email_body = f"""
                <html><body>
                    <p>Hello,</p>
                    <p>Your one-time login code is: <strong>{login_code}</strong></p>
                    <p>This code will expire in <strong>{minutes_to_expire} minutes</strong>.</p>
                    <p>If you did not request this code, you can safely ignore this email.</p>
                    <br>
                    <p>Thank you,<br><em>BU Reporting Team</em></p>
                </body></html>
                """
                if not send_email(to_email=email, subject=email_subject, html_content=email_body):
                    logger.error(f"Failed to send login code email to: {email}")
                    raise Exception("Failed to send the login code email.")
                self.db.commit()
                logger.info(f"Login code sent and committed for email: {email}")
        except pymssql.Error as ex:
            logger.error(f"Database error in request_login_code: {ex}")
            raise
        except Exception as e:
            logger.error(f"Service error in request_login_code: {e}")
            raise
        return {"message": "A login code has been sent to your email. Please check your inbox."}

    def verify_login_and_get_user(self, email: str, code: str) -> Dict[str, Any]:
        if not re.match(EMAIL_REGEX, email):
            logger.warning(f"Invalid email format attempted: {email}")
            raise ValueError("Invalid email format provided.")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_verify_login_code', (email, code))
                user_data = cursor.fetchone()
                logger.info(f"verify_login_and_get_user: user_data fetched: {user_data}")

                if not user_data or not user_data.get('email_exists', False):
                    logger.warning(f"Email not found: {email}. user_data: {user_data}")
                    raise EmailNotFoundError("Email not found.")

                if not user_data.get('is_active', False):
                    logger.warning(f"User is not active: {email}. user_data: {user_data}")
                    raise UserNotActiveError("User is not active.")

                if user_data.get('user_id',0) <= 0:
                    logger.warning(f"Invalid or expired login code for email: {email}. user_data: {user_data}")
                    raise InvalidLoginCodeError("Invalid or expired login code.")

                user_id = user_data.get('user_id')
                if user_id is None:
                    logger.error(f"user_id missing in user_data: {user_data}")
                    raise Exception("user_id missing in user_data.")

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
                logger.info(f"User {user_id} ({email}) successfully logged in. Session data: {user_session_data}")
                return {
                    "user_id": user_id,
                    "status": "success",
                    "message": f"Welcome, {first_name}!",
                    "data": user_session_data
                }
        except pymssql.Error as ex:
            logger.error(f"Database error in verify_login_and_get_user: {ex}")
            raise
        except (EmailNotFoundError, UserNotActiveError, InvalidLoginCodeError):
            raise
        except Exception as e:
            logger.error(f"Service error in verify_login_and_get_user: {e}", exc_info=True)
            raise