import pymssql
import logging
from queue import Queue, Empty, Full
from contextlib import contextmanager
from config import settings


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db_pool = Queue(maxsize=settings.DB_POOL_SIZE)

def _create_connection():
    try:
        return pymssql.connect(
            server=settings.DB_SERVER,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_DATABASE
        )
    except pymssql.Error as ex:
        logging.error(f"Failed to create a new database connection: {ex}")
        raise

def initialize_pool():
    if not db_pool.empty():
        logging.info("Pool is already initialized.")
        return
    for _ in range(settings.DB_POOL_SIZE):
        try:
            db_pool.put_nowait(_create_connection())
        except Full:
            break
    logging.info(f"Database connection pool initialized with {db_pool.qsize()} connections.")

def close_pool():
    while not db_pool.empty():
        try:
            conn = db_pool.get_nowait()
            conn.close()
        except Empty:
            break
    logging.info("Database connection pool gracefully closed.")

@contextmanager
def get_db_connection():
    conn_to_yield = None
    try:
        conn_from_pool = db_pool.get(timeout=2)

        try:
            with conn_from_pool.cursor() as cursor:
                cursor.execute("SELECT 1")
            conn_to_yield = conn_from_pool
        except pymssql.Error:
            logging.warning("Stale connection detected. Closing and replacing.")
            try:
                conn_from_pool.close()
            except pymssql.Error:
                pass
            
            conn_to_yield = _create_connection()
        
        yield conn_to_yield

    except Empty:
        logging.error("Could not get a database connection from the pool. Pool is empty and timeout exceeded.")
        raise
    finally:
        if conn_to_yield:
            try:
                db_pool.put_nowait(conn_to_yield)
            except Full:
                logging.warning("Connection pool is full. Closing surplus connection.")
                conn_to_yield.close()

def get_db():
    with get_db_connection() as conn:
        yield conn