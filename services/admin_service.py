
import pymssql
from typing import Dict, Any
from config import logger
from helpers import fetch_data
from exceptions import ReportingPeriodError


class AdminService:
    def __init__(self, db: pymssql.Connection):
        self.db = db


    def fetch_okr_submissions(self, user_id: int) -> Any:
        logger.info(f"Fetching OKR submissions for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_submissions", params=(user_id,))


    def close_reporting_period(self, user_id: int) -> Dict[str, Any]:
        logger.info(f"Closing reporting period for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_close_reporting_period', (user_id,))
                result = cursor.fetchone()
            self.db.commit()
            if not result or "status" not in result:
                logger.error(f"No status returned from usp_close_reporting_period for user {user_id}")
                raise ReportingPeriodError("No status returned from stored procedure.")
            logger.info(f"Reporting period close result for user {user_id}: {result}")
            return {"status": "success", "message": "Reporting period closed successfully."}
        except pymssql.Error as ex:
            logger.error(f"Database error while closing report period for user {user_id}: {ex}")
            raise
        except ReportingPeriodError:
            raise
        except Exception as e:
            logger.error(f"Error in close_reporting_period: {e}")
            raise


    def set_reporting_period(self, year: int, month: int, user_id: int) -> Dict[str, str]:
        logger.info(f"Setting reporting period to {year}/{month} for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_set_reporting_period', (year, month, user_id))
                result = cursor.fetchone()
            self.db.commit()
            if not result or "status" not in result:
                logger.error(f"No status returned from usp_set_reporting_period for user {user_id}")
                raise ReportingPeriodError("No status returned from stored procedure.")
            return result
        except pymssql.Error as ex:
            logger.error(f"Database error while setting reporting period for user {user_id}: {ex}")
            raise
        except (ReportingPeriodError, ValueError):
            raise
        except Exception as e:
            logger.error(f"Error in set_reporting_period: {e}")
            raise
