import pymssql
import logging
from helpers import send_email

def request_login_code(db: pymssql.Connection, email: str):
    try:
        with db.cursor() as cursor:
            sql = "DECLARE @code_out NCHAR(6); EXEC usp_generate_login_code @email=%s, @plainTextCode=@code_out OUTPUT; SELECT @code_out;"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()

            if result and result[0]:
                plain_text_code = result[0]
                
        if plain_text_code:
            email_subject = "Your One-Time Login Code"
            email_body = f"""
            <html>
                <body>
                    <p>Hello,</p>
                    <p>Your one-time login code is: <strong>{plain_text_code}</strong></p>
                    <p>This code will expire in 60 minutes.</p>
                    <p>If you did not request this code, you can safely ignore this email.</p>
                    <p>Thank you,<br>BU Reporting Team</p>
                </body>
            </html>
            """
            
            send_email(to_email=email, subject=email_subject, html_content=email_body)
        
            db.commit()
            
    except pymssql.Error as ex:
        logging.error(f"Database Service Error in request_login_code: {ex}")
        raise
            
    return {"message": "A login code has been sent to your email. Please check your inbox."}


def verify_login_and_get_user(db: pymssql.Connection, email: str, code: str):
    try:
        with db.cursor(as_dict=True) as cursor:
            cursor.callproc('usp_verify_login_code', (email, code))
            user_data = cursor.fetchone()
            
            if user_data and user_data.get('user_id') > 0:
                user_id = user_data['user_id']
                first_name = user_data['first_name']

                cursor.callproc('usp_get_user_permissions', (user_id,))
                permissions = cursor.fetchall()

                db.commit()

                return {
                    "user_id": user_id,
                    "status": "success",
                    "message": f"Welcome {first_name}!",
                    "permissions": permissions
                    }
            else:
                return {"user_id": 0, "status": "failed", "message": "Invalid or expired login code."}        
    except pymssql.Error as ex:
        print(f"Database Service Error in verify_login_and_get_user: {ex}")
        raise