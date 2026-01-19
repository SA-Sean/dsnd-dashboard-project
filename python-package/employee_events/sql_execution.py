from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Using pathlib, create a `db_path` variable
# that points to the absolute path for the `employee_events.db` file
cwd = Path(__file__).parent
db_path = cwd / 'employee_events.db'


# OPTION 1: MIXIN
# Define a class called `QueryMixin`
class QueryMixin:


    # Define a method named `pandas_query`
    # that receives an sql query as a string
    # and returns the query's result
    # as a pandas dataframe
    def pandas_query(sql_query:str) -> pd.DataFrame:

        """
        Excutes and SQL query against a database connection and returns the result as a padas dataframe
        
        """

        try:
            # establish db connection
            db_conn = connect(db_path)

            # query database and return result as dataframe
            sql_result = pd.read_sql_query(sql_query, db_conn)
            
            # close database connection
            db_conn.close()
        
            return sql_result # return pandas dataframe with query result data

        except Exception as e:
            
            # catch and show any errors that occure in the DB interaction
            print(f"An error with the database interaction occurred: {e}")

            return pd.DataFrame()   # return empty dataframe on failure
        

    # Define a method named `query`
    # that receives an sql_query as a string
    # and returns the query's result as
    # a list of tuples. (You will need
    # to use an sqlite3 cursor)
def query(sql_query:str):

    """
    Excutes and SQL query against a database connection and returns the result as a list of tuples

    """
    
    try:
        # establish db connection
        db_conn = connect(db_path)

        # create cursor object to run the query
        cursor = db_conn.cursor()

        # execute the query
        cursor.execute(sql_query)

        # fetch all the results as a list of tuples
        result = cursor.fetchall()

        # close db connection
        db_conn.close()

        return result

    except Exception as e:

            # catch and show any errors that occure in the DB interaction
            print(f"An error with the database interaction occurred: {e}")

            return pd.DataFrame()   # return empty dataframe on failure

 
 # Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    
    return run_query


