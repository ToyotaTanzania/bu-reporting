import pymssql
from config import logger
from helpers import fetch_data, update_items_from_xml, execute_proc_for_xml, create_custom_presentation_from_xml

class ReportingService:
    def __init__(self, db: pymssql.Connection):
        self.db = db

    def fetch_business_units(self, user_id: int):
        logger.info(f"Fetching business units for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_business_units", params=(user_id,))

    def fetch_okrs(self, user_id: int):
        logger.info(f"Fetching OKRs for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_details", params=(user_id,))

    def fetch_okr_tracker_by_user(self, user_id: int):
        logger.info(f"Fetching OKR tracker for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_okr_tracker_by_user", params=(user_id,))

    def fetch_kjops_by_user(self, user_id: int):
        logger.info(f"Fetching KJ OPS for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_kjops_by_user", params=(user_id,))

    def fetch_commentaries(self, user_id: int):
        logger.info(f"Fetching commentaries for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_commentary_details", params=(user_id,))

    def fetch_priorities(self, user_id: int):
        logger.info(f"Fetching priorities for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_priorities", params=(user_id,))

    def fetch_priority_statuses(self):
        logger.info("Fetching priority statuses")
        return fetch_data(db=self.db, proc_name="usp_get_priority_statuses", params=())

    def fetch_tracker_statuses(self, user_id: int):
        logger.info(f"Fetching tracker statuses for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_ops_tracker_statuses", params=(user_id,))

    def fetch_overdues(self, user_id: int):
        logger.info(f"Fetching overdues for user {user_id}")
        return fetch_data(db=self.db, proc_name="usp_get_ops_overdues", params=(user_id,))

    def fetch_monthly_presentation(self, user_id: int, business_unit: str = None):
        logger.info(f"Initiating custom PowerPoint report for user {user_id}" + (f", business_unit={business_unit}" if business_unit else ""))
        params = (user_id,) if business_unit is None else (user_id, business_unit)
        xml_data = execute_proc_for_xml(
            db=self.db,
            proc_name='usp_generate_monthly_report_xml',
            params=params
        )
        if not xml_data:
            xml_data = "<root></root>"
        return create_custom_presentation_from_xml(xml_string=xml_data)
    

    def bulk_update_okrs(self, xml_string: str, user_id: int):
        logger.info(f"Bulk updating OKRs for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="okr_details", xml_string=xml_string, user_id=user_id, item_name="OKRs")

    def bulk_update_commentaries(self, xml_string: str, user_id: int):
        logger.info(f"Bulk updating commentaries for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="commentary_details", xml_string=xml_string, user_id=user_id, item_name="KJ OPS")

    def bulk_update_priorities(self, xml_string: str, user_id: int):
        logger.info(f"Bulk updating priorities for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="priorities", xml_string=xml_string, user_id=user_id, item_name="Priorities")

    def bulk_update_tracker_statuses(self, xml_string: str, user_id: int):
        logger.info(f"Bulk updating tracker statuses for user {user_id}")
        return update_items_from_xml(db=self.db, table_name="ops_tracker_statuses", xml_string=xml_string, user_id=user_id, item_name="Tracker Statuses")

    def bulk_update_overdues(self, xml_string: str, user_id: int):
        logger.info(f"Bulk updating overdues for user {user_id}")

        return update_items_from_xml(db=self.db, table_name="ops_overdues", xml_string=xml_string, user_id=user_id, item_name="Overdues")
