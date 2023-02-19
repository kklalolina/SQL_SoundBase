from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for
from soundbase.auth import login_required, admin_login_required
import cx_Oracle
from soundbase.db_constants import ADMIN_TYPE, NORMAL_TYPE
from soundbase.db import requires_db_connection
import soundbase.db as db
bp = Blueprint("views_soundbaseUser", __name__)


@bp.route('/release/<id>')
def release():
    return

@bp.route('/artists/list')
def artistsList():
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT ROWNUM, ARTIST_ID, ARTIST_NAME FROM ARTIST")
    artists = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("user/artist/list.html", artists=artists)

@bp.route('/artists/<id>')
def artist(id):
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ARTIST WHERE ARTIST_ID = :x",x=id)
    data = cursor.fetchone()

    cursor.execute("SELECT ROWNUM, RELEASE_NAME, RELEASE_DATE FROM ARTIST_OF_RELEASE ar JOIN MUSIC_RELEASE m on ar.RELEASE_ID=m.RELEASE_ID WHERE ARTIST_ID=:x ",x=id)
    releases = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("user/artist/details.html", output=data, releases=releases)


@bp.route('/genres')
def genresList():
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT ROWNUM, GENRE_NAME, GENRE_DESCRIPTION FROM GENRE")
    genres = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("user/genre/list.html", genres=genres)

@bp.route('/tags')
def tagsList():
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT ROWNUM, TAG_NAME, TAT_DESCRIPTION FROM DESCRIPTIVE_TAG ")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("user/tag/list.html", tags=tags)


