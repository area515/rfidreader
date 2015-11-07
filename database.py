import MySQLdb
import os

class Connection(object):

    def __init__(self, user, password, host, db_name):

        self.user = user
        self.password = password
        self.host = host
        self.db_name = db_name
        self.db = None

    def connect(self):

        self.db = MySQLdb.connect(host=self.host, user=self.user,
                                  password=self.password, db=self.db_name)

    def cursor(self):

        if self.db:
            return self.db.cursor()


REFRESH_QUERY = "Select * from USERS"


def write_user_list(user_list_file, rows):

    if not rows:
        print 'No rows'

    if not user_list_file:
        print 'no user list file defined'

    with open(user_list_file) as user_file:

        pass


def refresh_user_list():

    user = os.getenv('WP_USER')
    password = os.getenv('WP_PASSWORD')
    host = os.getenv('WP_HOST')
    db_name = os.getenv('WP_DB_NAME')

    connection = Connection(user, password, host, db_name)

    cursor = connection.cursor()

    cursor.execute(REFRESH_QUERY)

    write_user_list(cursor.fetchall())
