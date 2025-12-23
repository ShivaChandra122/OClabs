import polars as pl
import duckdb
from core.database import get_duckdb_connection
from typing import Optional

class DataEngine:
    """
    Manages data extraction and processing using DuckDB and Polars LazyFrames.
    Provides reusable and composable pipelines for data preparation.
    """

    def __init__(self):
        self._duckdb_con: Optional[duckdb.DuckDBPyConnection] = None

    def _get_duckdb_connection(self):
        """Ensures a single DuckDB connection is used and initialized."""
        if self._duckdb_con is None:
            self._duckdb_con = get_duckdb_connection()
        return self._duckdb_con

    def get_transaction_history_lazyframe(self) -> pl.LazyFrame:
        """
        Fetches transaction history data as a Polars LazyFrame.
        Normalizes schema. No business logic.
        """
        con = self._get_duckdb_connection()
        # Assuming 'transactions' is a table in your MySQL database
        # which DuckDB can now scan via the 'mysql_db' attachment.
        query = "SELECT * FROM mysql_db.transactions"
        
        # Use DuckDB to directly query and then convert to Polars LazyFrame
        # DuckDB's .pl().lazy() method is ideal here.
        lf = con.execute(query).pl().lazy()

        # Example schema normalization (adjust based on actual MySQL schema)
        # Ensure column names and types are consistent.
        lf = lf.select(
            pl.col("transaction_id").cast(pl.Utf8).alias("transaction_id"),
            pl.col("customer_id").cast(pl.Utf8).alias("customer_id"),
            pl.col("product_id").cast(pl.Utf8).alias("product_id"),
            pl.col("purchase_date").cast(pl.Datetime).alias("purchase_date"),
            pl.col("amount").cast(pl.Float64).alias("amount"),
            pl.col("quantity").cast(pl.Int64).alias("quantity"),
            # Add other relevant transaction columns and cast them appropriately
        )
        return lf

    def get_customer_metadata_lazyframe(self) -> pl.LazyFrame:
        """
        Fetches customer metadata as a Polars LazyFrame.
        Normalizes schema. No business logic.
        """
        con = self._get_duckdb_connection()
        # Assuming 'customers' is a table in your MySQL database
        query = "SELECT * FROM mysql_db.customers"

        lf = con.execute(query).pl().lazy()

        # Example schema normalization (adjust based on actual MySQL schema)
        lf = lf.select(
            pl.col("customer_id").cast(pl.Utf8).alias("customer_id"),
            pl.col("name").cast(pl.Utf8).alias("customer_name"),
            pl.col("email").cast(pl.Utf8).alias("customer_email"),
            pl.col("registration_date").cast(pl.Date).alias("registration_date"),
            # Add other relevant customer columns and cast them appropriately
        )
        return lf
    
    def get_product_metadata_lazyframe(self) -> pl.LazyFrame:
        """
        Fetches product metadata as a Polars LazyFrame.
        Normalizes schema. No business logic.
        """
        con = self._get_duckdb_connection()
        query = "SELECT * FROM mysql_db.products"

        lf = con.execute(query).pl().lazy()

        lf = lf.select(
            pl.col("product_id").cast(pl.Utf8).alias("product_id"),
            pl.col("product_name").cast(pl.Utf8).alias("product_name"),
            pl.col("category").cast(pl.Utf8).alias("category"),
            pl.col("price").cast(pl.Float64).alias("price"),
            # Add other relevant product columns
        )
        return lf

    def close_connection(self):
        """Closes the DuckDB connection if it's open."""
        if self._duckdb_con:
            self._duckdb_con.close()
            self._duckdb_con = None

# Example usage (for testing purposes, not part of the class logic)
if __name__ == "__main__":
    data_engine = DataEngine()
    try:
        print("Fetching transaction history...")
        transactions_lf = data_engine.get_transaction_history_lazyframe()
        # Show schema and a few rows (eager collect for display only)
        print("Transaction History Schema:")
        print(transactions_lf.schema)
        # For demonstration, limiting to 5 rows and collecting
        print("First 5 rows of Transaction History (LazyFrame collected):")
        print(transactions_lf.head(5).collect())

        print("\nFetching customer metadata...")
        customers_lf = data_engine.get_customer_metadata_lazyframe()
        print("Customer Metadata Schema:")
        print(customers_lf.schema)
        print("First 5 rows of Customer Metadata (LazyFrame collected):")
        print(customers_lf.head(5).collect())
        
        print("\nFetching product metadata...")
        products_lf = data_engine.get_product_metadata_lazyframe()
        print("Product Metadata Schema:")
        print(products_lf.schema)
        print("First 5 rows of Product Metadata (LazyFrame collected):")
        print(products_lf.head(5).collect())

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        data_engine.close_connection()
