import sqlalchemy
import duckdb
from core.config import get_settings

settings = get_settings()

def get_mysql_engine():
    """
    Creates and returns a SQLAlchemy engine for MySQL connection.
    """
    db_settings = settings.db
    return sqlalchemy.create_engine(
        f"mysql+mysqlconnector://{db_settings.mysql_user}:{db_settings.mysql_password}@"
        f"{db_settings.mysql_host}:{db_settings.mysql_port}/{db_settings.mysql_database}"
    )

def get_duckdb_connection():
    """
    Initializes and returns a DuckDB connection, allowing it to scan MySQL tables.
    """
    con = duckdb.connect(database=':memory:', read_only=False)
    # Install and load the MySQL extension for DuckDB
    con.execute("INSTALL mysql; LOAD mysql;")

    # Attach MySQL database for scanning
    # Note: DuckDB's ATTACH command can use SQLAlchemy-style connection strings
    db_settings = settings.db
    mysql_conn_string = (
        f"mysql://{db_settings.mysql_user}:{db_settings.mysql_password}@"
        f"{db_settings.mysql_host}:{db_settings.mysql_port}/{db_settings.mysql_database}"
    )
    con.execute(f"ATTACH '{mysql_conn_string}' AS mysql_db (TYPE MYSQL);")
    return con

if __name__ == "__main__":
    # Example usage and basic test
    print("Testing database connections...")
    try:
        mysql_engine = get_mysql_engine()
        with mysql_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("SELECT 1")).scalar()
            print(f"MySQL connection successful: {result}")
    except Exception as e:
        print(f"MySQL connection failed: {e}")

    try:
        duckdb_con = get_duckdb_connection()
        # Attempt to list tables from the attached MySQL database
        tables = duckdb_con.execute("SHOW TABLES FROM mysql_db;").fetchdf()
        print("DuckDB connection successful. Tables from MySQL_db:")
        print(tables)
        duckdb_con.close()
    except Exception as e:
        print(f"DuckDB connection failed: {e}")
