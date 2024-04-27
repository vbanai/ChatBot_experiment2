import pandas as pd
import psycopg2
from psycopg2 import sql, extras
from psycopg2.extensions import register_adapter, AsIs
import numpy as np


def upload_to_ElephantSQL(database_url, table_name, new_df):
  register_adapter(np.int64, AsIs)
  # Convert DataFrame to records (list of tuples)
  records = [tuple(map(lambda x: int(x) if pd.notna(x) and isinstance(x, pd.Int64Dtype) else x, row)) for row in new_df.to_records(index=False)]


# Use psycopg2 to insert data into the PostgreSQL database
  with psycopg2.connect(database_url) as connection:
    with connection.cursor() as cursor:
      # Check if the table exists
      cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
      table_exists = cursor.fetchone()[0]

      if table_exists:
        # Drop the table if it exists
        cursor.execute(sql.SQL("DROP TABLE {} CASCADE;").format(sql.Identifier(table_name)))

      # Extract column names and data types from the DataFrame
      column_data_types = [
        (column, new_df[column].dtype.name) for column in new_df.columns
      ]

      # Map Pandas data types to PostgreSQL data types
      pg_data_types = {
        'int64': 'INTEGER',
        'object': 'VARCHAR',  # Assuming 'object' corresponds to text-like data
        # Add more mappings as needed for other Pandas data types
      }

      # Create the table
      create_table_query = sql.SQL("CREATE TABLE {} ({});").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(
            sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(pg_data_types[dtype]))
            for column, dtype in column_data_types
        )
      )

      cursor.execute(create_table_query)

      # Use execute_values to insert data efficiently
      columns = [column for column, _ in column_data_types]
      query = sql.SQL("INSERT INTO {} ({}) VALUES %s;").format(sql.Identifier(table_name), sql.SQL(', ').join(map(sql.Identifier, columns)))
      extras.execute_values(cursor, query, records)

    # Commit the changes
    connection.commit()