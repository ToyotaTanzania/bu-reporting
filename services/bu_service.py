import pymssql
import logging
from helpers import fetch_data, update_items_from_xml, execute_proc_for_xml, create_custom_presentation_from_xml

class ReportingService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def fetch_business_units(self, user_id: int):
        logging.info(f"Fetching business units for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_business_units", params=(user_id,))

    def fetch_okrs(self, user_id: int):
        logging.info(f"Fetching OKRs for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_details", params=(user_id,))

    def fetch_commentaries(self, user_id: int):
        logging.info(f"Fetching commentaries for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_commentary_details", params=(user_id,))

    def fetch_priorities(self, user_id: int):
        logging.info(f"Fetching priorities for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_priorities", params=(user_id,))

    def fetch_tracker_statuses(self, user_id: int):
        logging.info(f"Fetching tracker statuses for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_ops_tracker_statuses", params=(user_id,))

    def fetch_overdues(self, user_id: int):
        logging.info(f"Fetching overdues for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_ops_overdues", params=(user_id,))
    

    def bulk_update_okrs(self, xml_string: str, user_id: int):
        logging.info(f"Bulk updating OKRs for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="okr_details", xml_string=xml_string, user_id=user_id, item_name="OKRs")

    def bulk_update_commentaries(self, xml_string: str, user_id: int):
        logging.info(f"Bulk updating commentaries for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="commentary_details", xml_string=xml_string, user_id=user_id, item_name="KJ OPS")

    def bulk_update_priorities(self, xml_string: str, user_id: int):
        logging.info(f"Bulk updating priorities for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="ops_priorities", xml_string=xml_string, user_id=user_id, item_name="Priorities")

    def bulk_update_tracker_statuses(self, xml_string: str, user_id: int):
        logging.info(f"Bulk updating tracker statuses for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="ops_tracker_statuses", xml_string=xml_string, user_id=user_id, item_name="Tracker Statuses")

    def bulk_update_overdues(self, xml_string: str, user_id: int):
        logging.info(f"Bulk updating overdues for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="ops_overdues", xml_string=xml_string, user_id=user_id, item_name="Overdues")
    
    def create_monthly_presentation(self, user_id: int):
        logging.info(f"Initiating custom PowerPoint report for user {user_id}")
        xml_data = execute_proc_for_xml(
            db=self.db,
            proc_name='usp_generate_monthly_report_xml',
            params=(user_id,)
        )
        return create_custom_presentation_from_xml(xml_string=xml_data)
    
    def set_reporting_period(self, year: int, month: int, user_id: int):
        logging.info(f"Setting reporting period to {year}-{month} for user {user_id}")
        try:
            with self.db.cursor(as_dict=True) as cursor:
                cursor.callproc('usp_set_reporting_period', (year, month, user_id))
                self.db.commit()
            return {"status": "success", "message": f"Reporting period successfully set to {year}-{month}."}
        except pymssql.Error as e:
            logging.error(f"Database error while setting reporting period: {e}")
            return {"status": "error", "message": "Failed to set reporting period due to a database error."}
        except Exception as e:
            logging.error(f"Unexpected error while setting reporting period: {e}")
            return {"status": "error", "message": "An unexpected error occurred while setting the reporting period."}