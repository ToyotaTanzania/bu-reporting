
from datetime import datetime
import pymssql
from typing import Dict, Any
from config import logger
from helpers import fetch_data
from exceptions import SubmissionPeriodError


class AdminService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def close_submission_period(self, user_id: int, closed_at: datetime) -> Dict[str, Any]:
        logger.info(f"Closing submission period for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_close_submission_period', (user_id, closed_at))
                result = cursor.fetchone()
            self.db.commit()
            if not result or "status" not in result:
                logger.error(f"No status returned from usp_close_submission_period for user {user_id}")
                raise SubmissionPeriodError("No status returned from stored procedure.")
            logger.info(f"Submission period close result for user {user_id}: {result}")
            return result
        except pymssql.Error as ex:
            logger.error(f"Database error while closing submission period for user {user_id}: {ex}")
            raise
        except SubmissionPeriodError:
            raise
        except Exception as e:
            logger.error(f"Error in close_submission_period: {e}")
            raise


    def set_submission_period(self, year: int, month: int, user_id: int) -> Dict[str, str]:
        logger.info(f"Setting submission period to {year}/{month} for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_set_submission_period', (year, month, user_id))
                result = cursor.fetchone()
            self.db.commit()
            if not result or "status" not in result:
                logger.error(f"No status returned from usp_set_submission_period for user {user_id}")
                raise SubmissionPeriodError("No status returned from stored procedure.")
            return result
        except pymssql.Error as ex:
            logger.error(f"Database error while setting submission period for user {user_id}: {ex}")
            raise
        except (SubmissionPeriodError, ValueError):
            raise
        except Exception as e:
            logger.error(f"Error in set_submission_period: {e}")
            raise

    def open_submission_period(self, user_id: int) -> Dict[str, str]:
        logger.info(f"Opening submission period for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_open_submission_period', (user_id,))
                result = cursor.fetchone()
            self.db.commit()
            if not result or "status" not in result:
                logger.error(f"No status returned from usp_open_submission_period for user {user_id}")
                raise SubmissionPeriodError("No status returned from stored procedure.")
            return result
        except pymssql.Error as ex:
            logger.error(f"Database error while opening submission period for user {user_id}: {ex}")
            raise
        except (SubmissionPeriodError, ValueError):
            raise
        except Exception as e:
            logger.error(f"Error in open_submission_period: {e}")
            raise

    def fetch_okr_master_list(self, bu_id: int) -> Dict[str, Any]:
        logger.info(f"Fetching OKR master list for BU {bu_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_master_list", params=(bu_id,))

    def fetch_business_units_with_okrs(self, user_id: int) -> Dict[str, Any]:
        logger.info(f"Fetching business units with OKRs for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_business_units_with_okrs", params=(user_id,))