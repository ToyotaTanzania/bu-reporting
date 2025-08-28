import logging
import pymssql
from helpers import fetch_data


class AdminService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def set_reporting_period(self, year: int, month: int, user_id: int):
        logging.info(f"Setting reporting period to {month}/{year} for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_set_reporting_period', (year, month, user_id))
                self.db.commit()
            return {"status": "success", "message": f"Reporting period successfully set to {month}/{year}."}
        except pymssql.Error as ex:
            if "No changes were made" in str(ex):
                logging.info("Reporting period was not changed as it's the same as the current period.")
                return {"status": "unchanged", "message": "No changes were made to the reporting period."}
            else:
                logging.error(f"Database error while setting reporting period: {ex}")
                raise
        except Exception as e:
            logging.error(f"Unexpected error while setting reporting period: {e}")
            raise

    def fetch_okr_submissions(self):
            logging.info(f"Fetching okr submissions")
            return fetch_data(db=self.db, proc_name="usp_get_okr_submissions", params=())