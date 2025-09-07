import pymssql
from config import logger
from helpers import fetch_data


class AdminService:
    def __init__(self, db: pymssql.Connection):
        self.db = db


    def fetch_okr_submissions(self, user_id: int):
        logger.info(f"Fetching OKR submissions for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_submissions", params=(user_id,))

    def close_reporting_period(self, user_id: int):
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_close_reporting_period', (user_id,))
                result = cursor.fetchone()

            self.db.commit()

            if result and "status" in result:
                return result
            else:
                raise Exception("The stored procedure did not return a status message.")

        except pymssql.Error as ex:
            logger.error(f"Database error while closing report period for user {user_id}: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error in close_reporting_period: {e}")
            raise

    def set_reporting_period(self, year: int, month: int, user_id: int):
        logger.info(f"Setting reporting period to {year}/{month} for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_set_reporting_period', (year, month, user_id))
                result = cursor.fetchone()
            self.db.commit()
            if result and "status" in result:
                return result
            else:
                raise Exception("The stored procedure did not return a status message.")
        except pymssql.Error as ex:
            logger.error(f"Database error while setting reporting period for user {user_id}: {ex}")
            raise
        except Exception as e:
            logger.error(f"Error in set_reporting_period: {e}")
            raise
