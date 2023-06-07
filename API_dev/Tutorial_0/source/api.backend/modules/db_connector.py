import mysql.connector

class Database:
    def __init__(self, db_type=''):
        ''''''
        self.db_type = db_type

    def close(self,):
        '''
        Close Database connections
        '''

        try:

            self.cursor.close()
            self.conn.close()

        except Exception as e:
            print(e)
        

    def connect(self, host='', port=3306, db_name='', db_user='', db_pass=''):
        ''''''
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass

        if (self.db_type.upper() == "MYSQL"):
            # If db type of MySQL then setup MySQL connection
            self.mysql_connect()
         
    def mysql_connect(self,):
        ''''''
        # Establish a connection to the MySQL database
        self.conn = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )
        # Create a cursor object to interact with the database
        self.cursor = self.conn.cursor()

    def query_exec(self, query=''):
        ''''''
        # Execute a simple query
        self.cursor.execute(query)

        return self.cursor
    
    def query_fetch(self, query=''):
        ''''''
        rows = self.query_exec(query)
        return rows.fetchall()

    def commit(self):
        self.conn.commit()
