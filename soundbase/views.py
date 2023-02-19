from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for
from soundbase.auth import login_required, admin_login_required, admin_not_allowed
import cx_Oracle
from soundbase.db_constants import ADMIN_TYPE, NORMAL_TYPE
from soundbase.db import requires_db_connection
import soundbase.db as db

bp = Blueprint("views", __name__)

@bp.route('/', methods=['GET', 'POST'])
@requires_db_connection
@admin_not_allowed
def index():
    try:
        g.db = db.Database()
    except cx_Oracle.Error:
        # Error connection to database view
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

                if searchgenre:
                    temp = g.db.select_from_table("GENRE_OF_RELEASE",
                                                  select_list=["RELEASE_ID"],
                                                  where_list=[{"GENRE_ID": searchgenre}])[0]

                    releasesids = [x[0] for x in temp]
                    rows=[]
                    for i in releasesids:
                        temp = g.db.select_from_table(["MUSIC_RELEASE", "RELEASE_TYPE"],
                                                      select_list=["RELEASE_ID", "RELEASE_NAME", "RELEASE_DATE",
                                                                   "TYPE_NAME"],
                                                      join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")],
                                                      where_list=[{"RELEASE_ID":i}])[0]
                        rows.append(temp[0])
                elif searchtag:
                    temp = g.db.select_from_table("TAG_OF_RELEASE",
                                                  select_list=["RELEASE_ID"],
                                                  where_list=[{"TAG_ID": searchtag}])[0]
                    releasesids = [x[0] for x in temp]
                    rows=[]
                    for i in releasesids:
                        temp = g.db.select_from_table(["MUSIC_RELEASE", "RELEASE_TYPE"],
                                                      select_list=["RELEASE_ID", "RELEASE_NAME", "RELEASE_DATE",
                                                                   "TYPE_NAME"],
                                                      join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")],
                                                      where_list=[{"RELEASE_ID": i}])[0]
                        rows.append(temp[0])
                else:
                    search = request.form['SearchString']
                    rows = g.db.select_from_table(["MUSIC_RELEASE", "RELEASE_TYPE"],
                                                  select_list=["RELEASE_ID", "RELEASE_NAME", "RELEASE_DATE",
                                                               "TYPE_NAME"],
                                                  join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")],
                                                  where_list=[{"%RELEASE_NAME":search}])[0]


                artists_id = {}
                for row in rows:
                    temp = g.db.select_from_table("ARTIST_OF_RELEASE",
                                                  select_list=["ARTIST_ID"],
                                                  where_list=[{"RELEASE_ID": row[0]}])[0]
                    artists_id[row[0]] = [x[0] for x in temp]
                artists = {}

                for i in artists_id:
                    chars = 0
                    artists[i] = []
                    for j in artists_id[i]:
                        if chars > 20:
                            artists[i].append('...')
                            break
                        temp = g.db.select_from_table("ARTIST",
                                                      select_list=["ARTIST_NAME"],
                                                      where_list=[{"ARTIST_ID": j}])[0][0]
                        if len(artists[i]) == len(artists_id[i]) - 1:
                            artists[i].append(temp[0])
                        else:
                            artists[i].append(temp[0] + ',')
                        chars += len(artists[i][-1])

                genres = g.db.select_from_table("GENRE")[0]

                tags = g.db.select_from_table("DESCRIPTIVE_TAG")[0]


                return render_template("user/index.html", output=rows, artists=artists, genres=genres, tags=tags)




            rows = g.db.select_from_table(["MUSIC_RELEASE","RELEASE_TYPE"],
                                                 select_list=["RELEASE_ID","RELEASE_NAME","RELEASE_DATE","TYPE_NAME"],
                                                 join_list=[("RELEASE_TYPE_ID","TYPE_ID","INNER")])[0]



            artists_id = {}
            for row in rows:
                temp = g.db.select_from_table("ARTIST_OF_RELEASE",
                                              select_list=["ARTIST_ID"],
                                              where_list=[{"RELEASE_ID":row[0]}])[0]
                artists_id[row[0]] = [x[0] for x in temp]
            artists = {}

            for i in artists_id:
                chars = 0
                artists[i] = []
                for j in artists_id[i]:
                    if chars > 20:
                        artists[i].append('...')
                        break
                    temp = g.db.select_from_table("ARTIST",
                                                  select_list=["ARTIST_NAME"],
                                                  where_list=[{"ARTIST_ID": j}])[0][0]
                    if len(artists[i]) == len(artists_id[i]) - 1:
                        artists[i].append(temp[0])
                    else:
                        artists[i].append(temp[0] + ',')
                    chars += len(artists[i][-1])


            genres = g.db.select_from_table("GENRE")[0]

            tags = g.db.select_from_table("DESCRIPTIVE_TAG")[0]

            averageratings = {}
            for i in rows:
                rating=g.db.select_average_of_release([i[0]])[0]
                averageratings[i[0]]=rating

            return render_template("user/index.html", output=rows, artists=artists, genres=genres, tags=tags, averageratings=averageratings)


@bp.route('/admin')
@admin_login_required
@requires_db_connection
def admin():
    return render_template("admin/index.html")




