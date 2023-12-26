import mysql.connector
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import os

host = os.getenv("host")
user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")


class MySQLDatabase:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def insert_data(self, table, columns, values):
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in values])})"
        
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Data inserted successfully")
            
            # Retrieve the latest created ID
            last_id = self.cursor.lastrowid
            print(f"Last inserted ID: {last_id}")
            
            return last_id
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        
    def fetch_all_rows(self, table):
        query = f"SELECT * FROM {table}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            if rows:
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                return df
            else:
                print(f"No data found in table {table}")
                return None

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        
    def get_row_count(self, table):
        query = f"SELECT COUNT(*) FROM {table}"

        try:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            return count

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

# db=MySQLDatabase()
# db.insert_data('booking', ['name'], ['SarmadAFzal'])


    def cancelled_count(self):
        query = f"SELECT count(*) FROM booking where is_cancel = 1"

        try:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            return count

           
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None


    def update_data(self, table, column, value, condition_column=None, condition_value=None):
        """
        Update data in the specified table.
        
        Parameters:
        - table (str): The name of the table.
        - column (str): The column to be updated.
        - value: The new value to set in the specified column.
        - condition_column (str, optional): The column for the WHERE condition.
        - condition_value (any, optional): The value for the WHERE condition.
        """
        query = f"UPDATE {table} SET {column} = %s"
        params = [value]

        if condition_column and condition_value:
            query += f" WHERE {condition_column} = %s"
            params.append(condition_value)

        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("Data updated successfully")
        except mysql.connector.Error as err:
            print(f"Error: {err}")