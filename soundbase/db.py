import os
import click
from flask import current_app, g
import oracledb


class Database:
    connection = None

    def __init__(self):
        # TODO: This probably will not work for you, check your pluggable database name and replace dbpl with it
        print("Connecting to", "127.0.0.1:1521/dbpl")

        connection = oracledb.connect("entryuser/entrypass@127.0.0.1:1521/dbpl")

    #TODO: NEEDS TO BE TESTED!!
    def select_average_of_release(self, release):
        cursor = self.connection.cursor()
        query = "SELECT AVG(STAR_VALUE) FROM RATING INNER JOIN MUSIC_RELEASE ON RATING.RATED_RELEASE_ID =" \
                " MUSIC_RELEASE.RELEASE_ID WHERE RELEASE_ID = :release"
        cursor.execute(query, release)
        rows = cursor.fetchone()
        cursor.close()

        return rows
    #TODO: NEEDS TO BE TESTED!!
    def select_search_artist(self, search):
        cursor = self.connection.cursor()
        if search.isDigit():
            cursor.execute("SELECT * FROM ARTIST WHERE ARTIST_ID = :search OR ARTIST_NAME LIKE %:search%", search)
        else:
            cursor.execute("SELECT * FROM ARTIST WHERE ARTIST_NAME LIKE %:search%", search)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # TODO: NEEDS TO BE TESTED!!
    def select_search_bar(self, keyword):
        query_artist = "SELECT * FROM ARTIST WHERE ARTIST_NAME=:keyword"
        query_release = "SELECT * FROM MUSIC_RELEASE WHERE ARTIST_NAME=:keyword"
        cursor = self.connection.cursor()
        rows = cursor.execute(query_artist, keyword)
        rows += cursor.execute(query_release, keyword)
        return rows

    # TODO: NEEDS TO BE TESTED!!
    def select_from_joined_table(self, tables, where_dict = {}):
        cursor = self.connection.cursor()
        if len(tables) > 3 or len(tables) < 2:
            raise Exception("Unsupported number of tables")
        if len(tables) == 2:
            query = "SELECT * FROM {0} NATURAL INNER JOIN {1}"
            arguments = where_dict.values()
            if not where_dict:
                cnt = 0
                query += " WHERE "
                for key in where_dict:
                    cnt += 1
                    query += "{0} = :val{1} AND ".format(key, 1)
                query = query[:-5] + ";"
        else:
            query = "SELECT * FROM {0} INNER NATURAL JOIN ({1} INNER NATURAL JOIN {2})"
            arguments = where_dict.values()
            if not where_dict:
                cnt = 0
                query += " WHERE "
                for key in where_dict:
                    cnt += 1
                    query += "{0} = :val{1} AND ".format(key, 1)
                query = query[:-5] + ";"
        cursor.execute(query, arguments)
        rows = cursor.fetchall()
        cursor.close()
        return rows


    # TODO: NEEDS TO BE TESTED!!!
    def select_from_table(self, table, where_dict={}):
        cursor = self.connection.cursor()
        query = "SELECT * FROM {0}".format(table)
        arguments = where_dict.values()

        if not where_dict:
            cnt = 0
            query += " WHERE "
            for key in where_dict:
                cnt += 1
                query += "{0} = :val{1} AND ".format(key, 1)
            query = query[:-5] + ";"

        cursor.execute(query, arguments)
        rows = cursor.fetchall()
        cursor.close()
        return rows

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
