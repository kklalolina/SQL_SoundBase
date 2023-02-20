import oracledb
from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for
from soundbase.auth import login_required, admin_login_required, admin_not_allowed
import cx_Oracle
from soundbase.db_constants import ADMIN_TYPE, NORMAL_TYPE
from soundbase.db import requires_db_connection
import soundbase.db as db
bp = Blueprint("views_soundbaseUser", __name__)


@bp.route('/release/<id>', methods=['POST','GET'])
@requires_db_connection
@admin_not_allowed
def release(id):
    if request.method=='POST': # Rating
        star = request.form['star']
        content = request.form['content']

        oldrating = g.db.select_from_table("RATING",
                                         where_list=[{"RATED_RELEASE_ID": id, "SOUNDBASE_USERS_ID":g.user[0]}])[0]

        if not oldrating:
            from datetime import date, datetime
            today = date.today()
            date = datetime.strptime(str(today), '%Y-%m-%d')
            g.db.call_procedure("ADD_RATING", [star, date, g.user[0], id, content])
            flash('Rating added successfully!')
        else:
            flash('Remove old rating to add a new one!')


    row = g.db.select_from_table("MUSIC_RELEASE",
                                  where_list=[{"RELEASE_ID": id}])[0][0]

    row = list(row)
    row[2]=str(row[2])[:10]
    print(row)

    tracks_id = g.db.select_from_table("TRACKS_IN_RELEASE",
                                 select_list=["TRACK_ID","TRACK_NO"],
                                 where_list=[{"RELEASE_ID": id}])[0]


    tracks_id = [[x[0],x[1]] for x in tracks_id]
    tracks = []

    for i in tracks_id:
        temp = g.db.select_from_table("TRACK",
                                      select_list=["TRACK_NAME","TRACK_LENGTH"],
                                      where_list=[{"TRACK_ID": i[0]}])[0][0]

        temp=list(temp)
        temp.insert(0,i[1])

        tracks.append(temp)

    artists_id = g.db.select_from_table("ARTIST_OF_RELEASE",
                                        select_list=["ARTIST_ID"],
                                        where_list=[{"RELEASE_ID": id}])[0]

    artists_id = [x[0] for x in artists_id]
    artists = []

    for i in artists_id:
        temp = g.db.select_from_table("ARTIST",
                                      select_list=["ARTIST_NAME"],
                                      where_list=[{"ARTIST_ID": i}])[0][0][0]
        artists.append(temp)


    genre_id = g.db.select_from_table("GENRE_OF_RELEASE",
                                  select_list=["GENRE_ID"],
                                  where_list=[{"RELEASE_ID": id}])[0][0][0]

    genre = g.db.select_from_table("GENRE",
                                      select_list=["GENRE_NAME"],
                                      where_list=[{"GENRE_ID": genre_id}])[0][0][0]


    tag_id = g.db.select_from_table("TAG_OF_RELEASE",
                                      select_list=["TAG_ID"],
                                      where_list=[{"RELEASE_ID": id}])[0][0][0]

    tag_name = g.db.select_from_table("DESCRIPTIVE_TAG",
                                   select_list=["TAG_NAME"],
                                   where_list=[{"TAG_ID": tag_id}])[0][0][0]


    type_name = g.db.select_from_table("RELEASE_TYPE",
                                      select_list=["TYPE_NAME"],
                                      where_list=[{"TYPE_ID": row[3]}])[0][0][0]



    ratings = g.db.select_from_table(["RATING","SOUNDBASE_USERS"],
                                    select_list=["USERNAME","STAR_VALUE","CONTENTS", "RATING_DATE","USER_ID","RATING_ID"],
                                    where_list=[{"RATED_RELEASE_ID": id}],
                                    join_list = [("SOUNDBASE_USERS_ID", "USER_ID", "INNER")])[0]

    for i in range(len(ratings)):
        ratings[i] = list(ratings[i])
        ratings[i][3] = str(ratings[i][3])[:10] # remove time from date

    averagestar = g.db.select_average_of_release([id])[0]
    print(averagestar)
    half=0
    if averagestar is not None:
        half=averagestar-int(averagestar)
        averagestar=int(averagestar)



    return render_template("user/release/releasedetails.html", release=row, artists=artists, genre=genre, tag=tag_name, type=type_name, tracks=tracks,ratings=ratings, averagestar=averagestar, half=half)

@bp.route('/artists/list')
@requires_db_connection
@admin_not_allowed
def artistsList():
    artists = g.db.select_from_table("ARTIST",
                                      select_list=["ROWNUM", "ARTIST_ID", "ARTIST_NAME"])[0]
    return render_template("user/artist/list.html", artists=artists)

@bp.route('/artists/<id>')
@requires_db_connection
@admin_not_allowed
def artist(id):


    data = g.db.select_from_table("ARTIST", where_list=[{"ARTIST_ID":id}])[0][0]


    releases = g.db.select_from_table(["ARTIST_OF_RELEASE", "MUSIC_RELEASE"],
                                     select_list=["ROWNUM", "RELEASE_NAME", "RELEASE_DATE"],
                                     where_list=[{"ARTIST_ID": id}],
                                     join_list=[("RELEASE_ID", "RELEASE_ID", "INNER")])[0]
    for i in range(len(releases)):
        releases[i] = list(releases[i])
        releases[i][2] = str(releases[i][2])[:10] # remove time from date

    return render_template("user/artist/details.html", output=data, releases=releases)


@bp.route('/genres')
@requires_db_connection
@admin_not_allowed
def genresList():

    genres = g.db.select_from_table("GENRE", select_list=["ROWNUM", "GENRE_NAME", "GENRE_DESCRIPTION"])[0]

    return render_template("user/genre/list.html", genres=genres)

@bp.route('/tags')
@requires_db_connection
@admin_not_allowed
def tagsList():

    tags = g.db.select_from_table("DESCRIPTIVE_TAG", select_list=["ROWNUM", "TAG_NAME", "TAT_DESCRIPTION"])[0]

    return render_template("user/tag/list.html", tags=tags)

@bp.route('/user/data', methods=['POST','GET'])
@requires_db_connection
@admin_not_allowed
@login_required
def userdata():
    if request.method=='POST':
        oldpassword = request.form['oldpassword']
        newpassword = request.form['password']
        cnewpassword = request.form['cpassword']

        error = None
        if not newpassword or not oldpassword:
            error = "Password is required."
        elif g.user[2]!=oldpassword:
            error = "Wrong current password!"
        elif len(newpassword) < 8 or not any(char.islower() for char in newpassword) or not any(char.isupper() for char in newpassword) or not any(char.isdigit() for char in newpassword):
            error = "New password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif newpassword != cnewpassword:
            error = "Passwords must match!"

        if error is None:
            session['password']=newpassword
            g.db.call_procedure("EDIT_USER",[g.user[0],g.user[1],g.user[2]])
            flash('Password changed successfully!')
        else:
            flash(error)

    return render_template("user/profile/userdata.html")

@bp.route('/user/ratings')
@requires_db_connection
@admin_not_allowed
@login_required
def ratings():
    userratings = g.db.select_from_table(["RATING","MUSIC_RELEASE"],
                                         select_list=["ROWNUM", "STAR_VALUE","RELEASE_NAME", "RATING_DATE","RATED_RELEASE_ID"],
                                         where_list=[{"SOUNDBASE_USERS_ID":g.user[0]}],
                                         join_list=[("RATED_RELEASE_ID","RELEASE_ID","INNER")])[0]

    for i in range(len(userratings)):
        userratings[i] = list(userratings[i])
        userratings[i][3] = str(userratings[i][3])[:10] # remove time from date

    return render_template("user/profile/ratings.html", output=userratings)

@bp.route('/user/playlists', methods=['GET', 'POST'])
@requires_db_connection
@admin_not_allowed
@login_required
def playlists():
    if request.method=='POST':
        playlist = request.form['playlistname']
        tag = request.form['tag']
        print(playlist)
        error=None
        if not playlist:
            error="Playlist name cant be empty!"

        if error is None:
            try:
                g.db.insert_into_table("RELEASE_LIST",
                                       {"AUTHOR_ID": g.user[0],
                                        "LIST_NAME": playlist,
                                        "CREATION_DATE": '01-JAN-11'})
                listid = g.db.select_from_table("RELEASE_LIST",
                                                select_list=["LIST_ID"],
                                                where_list=[{"LIST_NAME":playlist}])[0][0][0]
                g.db.insert_into_table("TAG_OF_LIST",
                                       {"LIST_ID": listid ,
                                        "TAG_ID": tag})
            except oracledb.IntegrityError:
                flash("Playlist name already taken!")
        else:
            flash(error)

    userplaylists = g.db.select_from_table("RELEASE_LIST",
                                         select_list=["ROWNUM","LIST_ID", "LIST_NAME", "CREATION_DATE"],
                                         where_list=[{"AUTHOR_ID": g.user[0]}])[0]

    for i in range(len(userplaylists)):
        userplaylists[i] = list(userplaylists[i])
        userplaylists[i][3] = str(userplaylists[i][3])[:10] # remove time from date

    tags = g.db.select_from_table("DESCRIPTIVE_TAG")[0]
    return render_template("user/profile/playlists.html",output=userplaylists,tags=tags)

@bp.route('/user/playlist/<id>')
@requires_db_connection
@admin_not_allowed
@login_required
def playlistdetails(id):

    playlist = g.db.select_from_table("RELEASE_LIST", where_list=[{"LIST_ID": id}])[0][0]

    releases_id = g.db.select_from_table("RELEASE_IN_LIST",
                                       select_list=["RELEASE_ID", "RELEASE_NO"],
                                       where_list=[{"LIST_ID": id}])[0]
    print(releases_id)
    releases_id = [[x[0], x[1]] for x in releases_id]
    rows = []

    for i in releases_id:
        temp = g.db.select_from_table(["MUSIC_RELEASE","RELEASE_TYPE"],
                                      select_list=["RELEASE_ID","RELEASE_NAME","TYPE_NAME"],
                                      where_list=[{"RELEASE_ID":i[0]}],
                                      join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")])[0][0]

        temp = list(temp)
        temp.insert(0, i[1])

        rows.append(temp)
        print(rows)
    artists_id = {}
    for row in rows:
        temp = g.db.select_from_table("ARTIST_OF_RELEASE",
                                             select_list=["ARTIST_ID"],
                                             where_list=[{"RELEASE_ID": row[1]}])[0]
        artists_id[row[1]] = [x[0] for x in temp]


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

    tag_id= g.db.select_from_table("TAG_OF_LIST",
                                   select_list=["TAG_ID"],
                                   where_list=[{"LIST_ID":id}])[0][0][0]
    tag = g.db.select_from_table("DESCRIPTIVE_TAG",
                                 select_list=["TAG_NAME"],
                                 where_list=[{"TAG_ID":tag_id}]
                                 )[0][0][0]
    return render_template("user/profile/playlistdetails.html",output=rows, artists=artists, playlist=playlist, tag=tag)

@bp.route('/rating/<rid>/delete/<id>')
@requires_db_connection
@admin_not_allowed
@login_required
def deleteRating(id, rid):
    g.db.call_procedure("DELETE_RATING", [id])
    return redirect(url_for('views_soundbaseUser.release',id=rid))

@bp.route('/playlist/delete/<id>')
@requires_db_connection
@admin_not_allowed
@login_required
def deletePlaylist(id):
    g.db.call_procedure("DELETE_RELEASE_LIST",[id])
    return redirect(url_for('views_soundbaseUser.playlists'))

@bp.route('/user/playlist/add/<id>', methods=['POST','GET'])
@requires_db_connection
@admin_not_allowed
@login_required
def addRelease(id):
    if request.method=='POST':
        playlistid = request.form['playlistid']


        # check if release is already in the playlist
        check = g.db.select_from_table("RELEASE_IN_LIST", where_list=[{"LIST_ID":playlistid, "RELEASE_ID":id}])[0]

        if not check:
            g.db.call_procedure("ADD_RELEASE_TO_LIST",[id,playlistid])

            flash('The release was successfully added!')
            return redirect(url_for('views.index'))
        else:
            flash('The release is already in the playlist!')
    release = g.db.select_from_table("MUSIC_RELEASE",
                                           select_list=["RELEASE_ID", "RELEASE_NAME"],
                                           where_list=[{"RELEASE_ID": id}])[0][0]

    userplaylists = g.db.select_from_table("RELEASE_LIST",
                                           select_list=["LIST_ID", "LIST_NAME", "CREATION_DATE"],
                                           where_list=[{"AUTHOR_ID": g.user[0]}])[0]
    print(userplaylists)
    if not userplaylists:
        flash('You dont have any playlists!')
        return redirect(url_for('views.index'))
    return render_template("user/profile/addrelease.html",playlists=userplaylists, release=release)

@bp.route('/user/playlist/<rid>/delete/<id>', methods=['POST','GET'])
@requires_db_connection
@admin_not_allowed
@login_required
def deleteRelease(id,rid):
    g.db.call_procedure("delete_release_from_list", [rid,id])
    return redirect(url_for('views_soundbaseUser.playlistdetails', id=id))