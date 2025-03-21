from database_connect import connect_database

# Test the connection
if __name__ == "__main__":
    conn = connect_database()
    if conn is not None:
        print("Connection to the database was successful!")
        conn.close()  # Close the connection after testing
    else:
        print("Failed to connect to the database.")
