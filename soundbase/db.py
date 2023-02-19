import functools
import oracledb
from flask import g, current_app as app
import soundbase.db_constants as db_constants



class Database:
    connection = None

    def __init__(self, user_type):
        print("Connecting to", "127.0.0.1:1522/sound...")
        # This probably will not work for you, check your pluggable database name and replace dbpl with it
        if user_type == db_constants.ENTRY_TYPE:
            print("...as entry.")
            self.connection = oracledb.connect("entryuser/entrypass@127.0.0.1:1522/sound")
        elif user_type == db_constants.NORMAL_TYPE:
            print("...as normal.")
            self.connection = oracledb.connect("normaluser/normalpass@127.0.0.1:1522/sound")
        elif user_type == db_constants.ADMIN_TYPE:
            print("...as admin.")
            self.connection = oracledb.connect("adminuser/adminpass@127.0.0.1:1522/sound")
        else:
            print("Wrong type - Connection failed")

    @staticmethod
    def get_cursor_dict(cursor):
        dictionary = {}
        column = 0
        for d in cursor.description:
            dictionary[d[0]] = column
            column = column + 1


        return dictionary

    def select_from_table(self, table, where_list=[], join_list=[], select_list=[]):
        cursor = self.connection.cursor()
        if type(select_list) is not list:
            if type(select_list) is str:
                select_list = [select_list]
            else:
                raise Exception("select_list must be a list or a string!")
        if not select_list:
            query = "SELECT * "
        else:
            query = "SELECT "
            for entry in select_list:
                query += "{0}, ".format(entry)
            query = query[:-2] + " "
        if type(table) is str:
            query += "FROM {0}".format(table)
        else:
            if len(join_list) != len(table) - 1:
                raise Exception("join_list dimensions do not match the number of tables!")
            query += "FROM "
            for idx, relation in enumerate(table):
                if idx == 0:
                    query += "{0} {1} JOIN ".format(relation, join_list[idx][2])
                else:
                    query += "{0} ON {1}.{2} = {0}.{3} ".format(relation, table[idx - 1],
                                                                join_list[idx - 1][0], join_list[idx - 1][1])
                    if idx + 1 != len(table):
                        query += "{0} JOIN ".format(join_list[idx][2])
        arguments = []

        def create_a_conjunction(where_dict):
            conjunction = ""
            for key in where_dict:
                if key[0] == '%':
                    conjunction += "{0} LIKE :{0} AND ".format(key[1:])
                    arguments.append("%{value}%".format(value=where_dict[key]))
                else:
                    conjunction += "{0} = :{0} AND ".format(key)
                    arguments.append(where_dict[key])
            return conjunction[:-5]

        if where_list:
            query += " WHERE "
            if type(where_list) is dict:
                query += create_a_conjunction(where_list)
            elif type(where_list) is list:
                for dictionary in where_list:
                    new_conjunction = create_a_conjunction(dictionary)
                    query += new_conjunction + " OR "
                query = query[:-4]

        cursor.execute(query, arguments)
        rows = cursor.fetchall()
        dictionary = self.get_cursor_dict(cursor)
        cursor.close()
        return rows, dictionary

    def insert_into_table(self, table, value_dict):
        cursor = self.connection.cursor()
        argument_values = list(value_dict.values())
        query = "INSERT INTO {0} ".format(table)
        schema = "("
        arguments = "("
        for key in value_dict:
            schema += "{0}, ".format(key)
            arguments += ":{0}, ".format(key)
        schema = schema[:-2] + ")"
        arguments = arguments[:-2] + ")"
        query += "{0} VALUES {1}".format(schema, arguments)
        cursor.execute(query, argument_values)
        self.connection.commit()
        cursor.close()

    def add_artist(self, name, startdate, descr):
        cursor = self.connection.cursor()
        cursor.callproc('ADD_ARTIST', [name, startdate, descr])
        self.connection.commit()
        cursor.close()

    def edit_artist(self, id, name, startdate, descr):
        cursor = self.connection.cursor()
        cursor.callproc('EDIT_ARTIST', [id, name, startdate, descr])
        self.connection.commit()
        cursor.close()

    def delete_artist(self, id):
        cursor = self.connection.cursor()
        cursor.callproc('DELETE_ARTIST', [id])
        self.connection.commit()
        cursor.close()

    def add_users(self, name, password):
        cursor = self.connection.cursor()
        cursor.callproc('ADD_USER', [name, password])
        self.connection.commit()
        cursor.close()

    def call_procedure(self, procedure_name, arguments):
        cursor = self.connection.cursor()
        if type(arguments) is not list:
            cursor.callproc(procedure_name, [arguments])
        else:
            cursor.callproc(procedure_name, arguments)
        self.connection.commit()
        cursor.close()

    # TODO: NEEDS TO BE TESTED!!
    def select_average_of_release(self, release):
        cursor = self.connection.cursor()
        query = "SELECT AVG(STAR_VALUE) FROM RATING INNER JOIN MUSIC_RELEASE ON RATING.RATED_RELEASE_ID =" \
                " MUSIC_RELEASE.RELEASE_ID WHERE RELEASE_ID = :release"
        cursor.execute(query, release)
        rows = cursor.fetchone()
        cursor.close()

        return rows

    def close_connection(self):
        self.connection.close()


def has_connection():
    return hasattr(g, "db")


def requires_db_connection(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            g.db = Database(-1)
        else:
            g.db = Database(g.user[3])
        return view(**kwargs)

    return wrapped_view
