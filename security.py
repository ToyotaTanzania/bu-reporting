from fastapi import Depends, HTTPException, Header
from typing import Optional
from database import get_db
import pymssql
from config import logger


def require_admin(
        x_user_id: Optional[int] = Header(None),
        db: pymssql.Connection = Depends(get_db)
) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        with db.cursor(as_dict=True) as cursor:
            cursor.callproc('usp_user_is_admin', (x_user_id,))
            result = cursor.fetchone()

            if not result or not result.get('is_admin'):
                raise HTTPException(status_code=403, detail="Forbidden: Administrator privileges required.")

    except pymssql.Error as ex:
        logger.error(f"Database error during admin permission check for user {x_user_id}: {ex}")
        raise HTTPException(status_code=500, detail="Database error during permission check.")

    return x_user_id