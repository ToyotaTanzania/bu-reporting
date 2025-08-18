import smtplib
import logging
import pymssql
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

def update_items_from_xml(db: pymssql.Connection, table_name: str, xml_string: str, user_id: int, item_name: str):
    """
    Executes the bulk update and returns a detailed success message,
    including a specific message when no changes are made.
    """
    try:
        with db.cursor(as_dict=True) as cursor:
            sql_command = "EXEC usp_bulk_update @tableName=%s, @xmlText=%s, @userID=%d"
            cursor.execute(sql_command, (table_name, xml_string, user_id))
            
            result = cursor.fetchone()
            affected_rows = result.get('AffectedRowCount', 0) if result else 0

        db.commit()
        
        if affected_rows > 0:
            message = f"Data processed for '{item_name}'. {affected_rows} row(s) were updated."
        else:
            message = "Operation successful, but no changes were made to the data."

        return {
            "status": "success",
            "message": message,
            "affected_rows": affected_rows
        }
    
    except pymssql.Error as ex:
        logging.error(f"Database Service Error in update_items_from_xml: {ex}")
        raise
    except Exception as e:
        logging.error(f"Generic Service Error in update_items_from_xml: {e}")
        raise

def fetch_data(db: pymssql.Connection, proc_name: str, params: tuple = ()):
    rows = []
    try:
        with db.cursor(as_dict=True) as cursor:
            cursor.callproc(proc_name, params)
            rows = cursor.fetchall()
    except pymssql.Error as ex:
        logging.error(f"Database Helper Error in fetch_data for '{proc_name}': {ex}")
        raise
    
    return rows

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using the smtp.office365.com SMTP server.
    Credentials are now sourced from the central settings object.
    """
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.SENDER_PASSWORD

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email, to_email, message.as_string()
            )
            logging.info(f"Email sent successfully to {to_email}.")
            return True
            
    except smtplib.SMTPAuthenticationError:
        logging.error("Failed to send email: SMTP Authentication failed. Check SENDER_EMAIL/SENDER_PASSWORD.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending email: {e}")
        return False