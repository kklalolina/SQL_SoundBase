from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for
from soundbase.auth import login_required, admin_login_required
import oracledb
from soundbase.db_constants import ADMIN_TYPE, NORMAL_TYPE
from soundbase.db import requires_db_connection
import soundbase.db as db

bp = Blueprint("views", __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    try:
        g.db = db.Database()
    except oracledb.Error:
        # Error connection to database view
        # TODO: I'm thinking we might need to check the validity of the db connection before every view. Should I write
        # TODO: a decorator for that?
        print("Can't connect to database.")
        return
    finally:
        if session.get('type') == ADMIN_TYPE:
            return redirect(url_for('views.admin'))
        else:
            if request.method == 'POST':
                try:
                    searchgenre = request.form['SearchGenre']
                except:
                    searchgenre = None
                try:
                    searchtag = request.form['SearchTag']
                except:
                    searchtag = None


                conn = oracledb.connect("entryuser/entrypass@localhost:1521/dbpl")
                cursor = conn.cursor()

                if searchgenre:
                    cursor.execute("SELECT RELEASE_ID FROM GENRE_OF_RELEASE WHERE GENRE_ID = :id", id=searchgenre)
                    releasesids = [x[0] for x in cursor.fetchall()]
                    rows=[]
                    for i in releasesids:
                        cursor.execute("SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID WHERE RELEASE_ID = :x",x=i)
                        rows.append(cursor.fetchone())
                elif searchtag:
                    cursor.execute("SELECT RELEASE_ID FROM TAG_OF_RELEASE WHERE TAG_ID = :id", id=searchtag)
                    releasesids = [x[0] for x in cursor.fetchall()]
                    rows=[]
                    for i in releasesids:
                        cursor.execute("SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID WHERE RELEASE_ID = :x",x=i)
                        rows.append(cursor.fetchone())
                else:
                    search = request.form['SearchString']
                    cursor.execute(
                    "SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID WHERE RELEASE_NAME LIKE :x",x='%'+search+'%')

                    rows = cursor.fetchall()

                artists_id = {}
                for row in rows:
                    cursor.execute("SELECT ARTIST_ID FROM ARTIST_OF_RELEASE WHERE RELEASE_ID = :id", id=row[0])
                    artists_id[row[0]] = [x[0] for x in cursor.fetchall()]
                artists = {}

                for i in artists_id:
                    chars = 0
                    artists[i] = []
                    for j in artists_id[i]:
                        if chars > 20:
                            artists[i].append('...')
                            break
                        cursor.execute("SELECT ARTIST_NAME FROM ARTIST WHERE ARTIST_ID = :id", id=j)
                        if len(artists[i]) == len(artists_id[i]) - 1:
                            artists[i].append(cursor.fetchone()[0])
                        else:
                            artists[i].append(cursor.fetchone()[0] + ',')
                        chars += len(artists[i][-1])

                cursor.execute("SELECT * FROM GENRE")
                genres = cursor.fetchall()

                cursor.execute("SELECT * FROM DESCRIPTIVE_TAG ")
                tags = cursor.fetchall()

                cursor.close()
                conn.close()
                return render_template("user/index.html", output=rows, artists=artists, genres=genres, tags=tags)

            conn = oracledb.connect("entryuser/entrypass@localhost:1521/dbpl")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID")

            rows = cursor.fetchall()

            artists_id = {}
            for row in rows:
                cursor.execute("SELECT ARTIST_ID FROM ARTIST_OF_RELEASE WHERE RELEASE_ID = :id", id=row[0])
                artists_id[row[0]] = [x[0] for x in cursor.fetchall()]
            artists = {}

            for i in artists_id:
                chars = 0
                artists[i] = []
                for j in artists_id[i]:
                    if chars > 20:
                        artists[i].append('...')
                        break
                    cursor.execute("SELECT ARTIST_NAME FROM ARTIST WHERE ARTIST_ID = :id", id=j)
                    if len(artists[i]) == len(artists_id[i]) - 1:
                        artists[i].append(cursor.fetchone()[0])
                    else:
                        artists[i].append(cursor.fetchone()[0] + ',')
                    chars += len(artists[i][-1])

            cursor.execute("SELECT * FROM GENRE")
            genres=cursor.fetchall()

            cursor.execute("SELECT * FROM DESCRIPTIVE_TAG ")
            tags = cursor.fetchall()

            cursor.close()
            conn.close()
            return render_template("user/index.html", output=rows, artists=artists, genres=genres, tags=tags)


@bp.route('/admin')
@admin_login_required
@requires_db_connection
def admin():
    return render_template("admin/index.html")




