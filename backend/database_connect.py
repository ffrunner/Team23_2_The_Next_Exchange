import psycopg2 
from database_config import config
 
#Function to connect postgres database 
def connect_database():
    connection = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        return connection
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            connection.close()
        return None
