import pymssql
from config import logger


class LogService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def create_log_entry(self, level: str, message: str, module_name: str, user_id: int, client_ip: str):
        try:
            with self.db.cursor() as cursor:
                params = (level, message, module_name, user_id)
                cursor.callproc('usp_insert_app_log', params)
            self.db.commit()
            return {"status": "success"}
        except pymssql.Error as ex:
            logger.error(f"Failed to create log entry: {ex}")
            return {"status": "failed"}