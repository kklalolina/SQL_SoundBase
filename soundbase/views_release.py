import oracledb
from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import admin_login_required
from soundbase.db import requires_db_connection

bp = Blueprint("views_release", __name__)


# ---------------------------------------SINGLE------------------------------------------------------
@bp.route('/releases', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def releases():
    if request.method == 'POST':
        search = request.form['SearchString']
        searchid = None
        if search.isdigit():
            searchid = search
        rows, names = g.db.select_from_table(["MUSIC_RELEASE", "RELEASE_TYPE"],
                                             select_list=["RELEASE_ID", "RELEASE_NAME", "RELEASE_DATE", "TYPE_NAME"],
                                             join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")],
                                             where_list=[{"RELEASE_ID": searchid}, {"%RELEASE_NAME": search},
                                                         {"%TYPE_NAME": search}])
        return render_template("admin/Release/list.html", output=rows)

    rows = g.db.select_from_table(["MUSIC_RELEASE", "RELEASE_TYPE"],
                                  select_list=["RELEASE_ID", "RELEASE_NAME", "RELEASE_DATE", "TYPE_NAME"],
                                  join_list=[("RELEASE_TYPE_ID", "TYPE_ID", "INNER")])[0]
    return render_template("admin/Release/list.html", output=rows)


@bp.route('/releases/createSingle', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def createSingle():  # po prostu wydanie z jedna piosenka - moze byc wiele artystow -----moze trzeba zmienic nazwe funkcji ale nie mam pomyslu
    if request.method == 'POST':
        # Get the tracks data from the form

        artists = request.form.getlist('artists')
        name = request.form['name']
        releasedate = request.form['date']

        genre = request.form['genre']
        tag = request.form['tag']

        trackname = request.form['trackname']
        hours = str(request.form['hours'])
        minutes = str(request.form['minutes'])
        seconds = str(request.form['seconds'])

        error = None
        from datetime import date, datetime
        try:
            if releasedate is not None and releasedate != "":
                releasedate = datetime.strptime(releasedate, '%Y-%m-%d')
        except:
            error = 'Date must be in format dd-mm-yyyy'
        if error is None:
            if not name:
                error = "Single name is required."
            elif not trackname:
                error = "Track name is required."
            elif releasedate is not None and releasedate != '' and releasedate.date() > date.today():
                error = "Date can't be from the future!"
            elif not artists:
                error = "Choose at least one artist!"
            elif not genre:
                error = "Choose genre!"
            elif not tag:
                error = "Choose tag!"

            # Formatting the track length to sql interval format
            days = '0'
            if int(hours) > 23:
                days = str(int(hours) // 24)
                hours = str(int(hours) % 24)
            if int(hours) < 10:
                hours = '0' + hours
            if int(minutes) < 10:
                minutes = '0' + minutes
            if int(seconds) < 10:
                seconds = '0' + seconds
            length = days + ' ' + hours + ':' + minutes + ':' + seconds

            # Connect to the database and add the new Release
            if error is None:
                type_id = g.db.select_from_table("RELEASE_TYPE",
                                                 where_list={"TYPE_NAME": "Single"},
                                                 select_list="TYPE_ID")[0][0][0]
                try:
                    g.db.call_procedure('ADD_MUSIC_RELEASE', [name, releasedate, type_id])
                except oracledb.IntegrityError:
                    flash("Integrity Error - Release name must be unique!")
                else:
                    release_id = g.db.select_from_table("MUSIC_RELEASE",
                                                        where_list={"RELEASE_NAME": name},
                                                        select_list="RELEASE_ID")[0][0][0]
                    g.db.call_procedure("ADD_TRACK", [trackname, length, release_id])
                    print(artists)
                    for i in artists:
                        print(i)
                        g.db.insert_into_table("ARTIST_OF_RELEASE",
                                               {"ARTIST_ID": i,
                                                "RELEASE_ID": release_id})
                    g.db.insert_into_table("GENRE_OF_RELEASE",
                                           {"GENRE_ID": genre,
                                            "RELEASE_ID": release_id})
                    g.db.insert_into_table("TAG_OF_RELEASE",
                                           {"TAG_ID": tag,
                                            "RELEASE_ID": release_id})
                    flash('Release added successfully!')
            else:
                flash(error)
        else:
            flash(error)

    artists = g.db.select_from_table("ARTIST", select_list=["ARTIST_ID", "ARTIST_NAME"])[0]
    genres = g.db.select_from_table("GENRE", select_list=["GENRE_ID", "GENRE_NAME"])[0]
    tags = g.db.select_from_table("DESCRIPTIVE_TAG", select_list=["TAG_ID", "TAG_NAME"])[0]

    return render_template("admin/Release/createSingle.html", artists=artists, genres=genres, tags=tags)


@bp.route('/releases/details/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def detailsSingle(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY

    release, release_names = g.db.select_from_table("MUSIC_RELEASE", where_list={"RELEASE_ID": id})
    release = release[0]

    track_id = g.db.select_from_table("TRACKS_IN_RELEASE", where_list={"RELEASE_ID": id})[0][0][1]

    track = g.db.select_from_table("TRACK", where_list={"TRACK_ID": track_id})[0][0]

    artists_id = g.db.select_from_table("ARTIST_OF_RELEASE", where_list={"RELEASE_ID": id})[0]

    artists_id = [x[0] for x in artists_id]
    artists = []

    for i in artists_id:
        artist = g.db.select_from_table("ARTIST", where_list={"ARTIST_ID": i}, select_list="ARTIST_NAME")[0][0][0]
        artists.append(artist)

    genre_id = g.db.select_from_table("GENRE_OF_RELEASE",
                                      where_list={"RELEASE_ID": id},
                                      select_list="GENRE_ID")[0][0][0]
    genre = g.db.select_from_table("GENRE",
                                   where_list={"GENRE_ID": genre_id},
                                   select_list="GENRE_NAME")[0][0][0]

    tag_id = g.db.select_from_table("TAG_OF_RELEASE",
                                    where_list={"RELEASE_ID": id},
                                    select_list="TAG_ID")[0][0][0]

    tag = g.db.select_from_table("DESCRIPTIVE_TAG",
                                 where_list={"TAG_ID": tag_id},
                                 select_list="TAG_NAME")[0][0][0]

    type_name = g.db.select_from_table("RELEASE_TYPE",
                                       where_list={"TYPE_ID": release[release_names["RELEASE_TYPE_ID"]]},
                                       select_list="TYPE_NAME")[0][0][0]

    return render_template("admin/Release/detailsSingle.html", release=release, genre=genre, artists=artists,
                           track=track, type=type_name, tag=tag)


# ------------------------------------------ALBUM---------------------------------------------------

@bp.route('/releases/createAlbum', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def createAlbum():
    if request.method == 'POST':
        # Get the tracks data from the form

        artists = request.form.getlist('artists')
        name = request.form['name']
        releasedate = request.form['date']

        genre = request.form['genre']
        tag = request.form['tag']

        error = None
        from datetime import date, datetime
        try:
            if releasedate is not None and releasedate != "":
                releasedate = datetime.strptime(releasedate, '%Y-%m-%d')
        except:
            error = 'Date must be in format dd-mm-yyyy'
        if error is None:
            if not name:
                error = "Single name is required."
            elif releasedate is not None and releasedate != '' and releasedate.date() > date.today():
                error = "Date can't be from the future!"
            elif not artists:
                error = "Choose at least one artist!"
            elif not genre:
                error = "Choose genre!"
            elif not tag:
                error = "Choose tag!"

            # Connect to the database and add the new Release
            if error is None:
                # ZAPEWNIC ZEBY TYPE ISTNIAL!!!!
                type_id = g.db.select_from_table("RELEASE_TYPE",
                                                 where_list={"TYPE_NAME": "Album"},
                                                 select_list="TYPE_ID")[0][0][0]

                try:
                    g.db.call_procedure('ADD_MUSIC_RELEASE', [name, releasedate, type_id])
                except oracledb.IntegrityError:
                    flash("Integrity Error - Release name must be unique!")
                else:
                    release_id = g.db.select_from_table("MUSIC_RELEASE",
                                                        where_list={"RELEASE_NAME": name},
                                                        select_list="RELEASE_ID")[0][0][0]

                    for i in artists:
                        print(i)
                        g.db.insert_into_table("ARTIST_OF_RELEASE",
                                               {"ARTIST_ID": i,
                                                "RELEASE_ID": release_id})
                    g.db.insert_into_table("GENRE_OF_RELEASE",
                                           {"GENRE_ID": genre,
                                            "RELEASE_ID": release_id})
                    g.db.insert_into_table("TAG_OF_RELEASE",
                                           {"TAG_ID": tag,
                                            "RELEASE_ID": release_id})
                    flash('Release added successfully!')
            else:
                flash(error)
        else:
            flash(error)

    artists = g.db.select_from_table("ARTIST", select_list=["ARTIST_ID", "ARTIST_NAME"])[0]
    genres = g.db.select_from_table("GENRE", select_list=["GENRE_ID", "GENRE_NAME"])[0]
    tags = g.db.select_from_table("DESCRIPTIVE_TAG", select_list=["TAG_ID", "TAG_NAME"])[0]
    return render_template("admin/Release/createAlbum.html", artists=artists, genres=genres, tags=tags)


@bp.route('/releases/<id>/addTrack', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def addTrack(id):
    if request.method == 'POST':
        # Get the tracks data from the form
        name = request.form['name']
        hours = str(request.form['hours'])
        minutes = str(request.form['minutes'])
        seconds = str(request.form['seconds'])
        # Formatting the track length to sql interval format
        days = '0'
        if int(hours) > 23:
            days = str(int(hours) // 24)
            hours = str(int(hours) % 24)
        if int(hours) < 10:
            hours = '0' + hours
        if int(minutes) < 10:
            minutes = '0' + minutes
        if int(seconds) < 10:
            seconds = '0' + seconds
        length = days + ' ' + hours + ':' + minutes + ':' + seconds

        error = None
        if not name:
            error = "Name is required."

        # Connect to the database and add the new Track
        if error is None:
            try:
                g.db.call_procedure('ADD_TRACK', [name, length, id])
            except oracledb.Error as ex:
                if ex.args[0].code == 20000:
                    flash("Too many tracks in album!")
                else:
                    flash(type(ex).__name__ + " has occurred! Details: ")
                    flash(ex)
            else:
                flash('Track added successfully!')
        else:
            flash(error)
    releasename = g.db.select_from_table("MUSIC_RELEASE",
                                         where_list={"%RELEASE_ID": id},
                                         select_list="RELEASE_NAME")[0][0][0]

    return render_template("admin/Release/addTrack.html", releasename=releasename)


@bp.route('/releases/album/<id>/details', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def detailsAlbum(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    release, release_names = g.db.select_from_table("MUSIC_RELEASE", where_list={"RELEASE_ID": id})
    release = release[0]

    tracks_id = g.db.select_from_table("TRACKS_IN_RELEASE",
                                       where_list={"RELEASE_ID": id},
                                       select_list="TRACK_ID")[0]

    tracks_id = [x[0] for x in tracks_id]
    tracks = []

    for i in tracks_id:
        track = g.db.select_from_table("TRACK",
                                       where_list={"TRACK_ID": i})[0][0]
        tracks.append(track)
    print(tracks)

    artists_id = g.db.select_from_table("ARTIST_OF_RELEASE", where_list={"RELEASE_ID": id})[0]

    artists_id = [x[0] for x in artists_id]
    artists = []

    for i in artists_id:
        artist = g.db.select_from_table("ARTIST", where_list={"ARTIST_ID": i}, select_list="ARTIST_NAME")[0][0][0]
        artists.append(artist)

    genre_id = g.db.select_from_table("GENRE_OF_RELEASE",
                                      where_list={"RELEASE_ID": id},
                                      select_list="GENRE_ID")[0][0][0]
    genre = g.db.select_from_table("GENRE",
                                   where_list={"GENRE_ID": genre_id},
                                   select_list="GENRE_NAME")[0][0][0]

    tag_id = g.db.select_from_table("TAG_OF_RELEASE",
                                    where_list={"RELEASE_ID": id},
                                    select_list="TAG_ID")[0][0][0]

    tag = g.db.select_from_table("DESCRIPTIVE_TAG",
                                 where_list={"TAG_ID": tag_id},
                                 select_list="TAG_NAME")[0][0][0]

    type_name = g.db.select_from_table("RELEASE_TYPE",
                                       where_list={"TYPE_ID": release[release_names["RELEASE_TYPE_ID"]]},
                                       select_list="TYPE_NAME")[0][0][0]
    return render_template("admin/Release/detailsAlbum.html", release=release, genre=genre, artists=artists,
                           tracks=tracks, type=type_name, tag=tag)


@bp.route('/releases/album/<idr>/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def deleteTrack(id, idr):
    g.db.call_procedure('DELETE_TRACK', [id])

    release, release_names = g.db.select_from_table("MUSIC_RELEASE",
                           where_list={"RELEASE_ID": idr})
    release = release[0]

    tracks_id = g.db.select_from_table("TRACKS_IN_RELEASE",
                                       where_list={"RELEASE_ID": idr},
                                       select_list="TRACK_ID")[0]

    tracks_id = [x[0] for x in tracks_id]
    tracks = []

    for i in tracks_id:
        track = g.db.select_from_table("TRACK",
                                       where_list={"TRACK_ID": i})[0][0]
        tracks.append(track)
    print(tracks)

    artists_id = g.db.select_from_table("ARTIST_OF_RELEASE", where_list={"RELEASE_ID": idr})[0]

    artists_id = [x[0] for x in artists_id]
    artists = []

    for i in artists_id:
        artist = g.db.select_from_table("ARTIST", where_list={"ARTIST_ID": i}, select_list="ARTIST_NAME")[0][0][0]
        artists.append(artist)

    genre_id = g.db.select_from_table("GENRE_OF_RELEASE",
                                      where_list={"RELEASE_ID": idr},
                                      select_list="GENRE_ID")[0][0][0]
    genre = g.db.select_from_table("GENRE",
                                   where_list={"GENRE_ID": genre_id},
                                   select_list="GENRE_NAME")[0][0][0]

    tag_id = g.db.select_from_table("TAG_OF_RELEASE",
                                    where_list={"RELEASE_ID": idr},
                                    select_list="TAG_ID")[0][0][0]

    tag = g.db.select_from_table("DESCRIPTIVE_TAG",
                                 where_list={"TAG_ID": tag_id},
                                 select_list="TAG_NAME")[0][0][0]

    type_name = g.db.select_from_table("RELEASE_TYPE",
                                       where_list={"TYPE_ID": release[release_names["RELEASE_TYPE_ID"]]},
                                       select_list="TYPE_NAME")[0][0][0]
    return render_template("admin/Release/detailsAlbum.html", release=release, genre=genre, artists=artists,
                           tracks=tracks, type=type_name)


# -----------------------delete any release------------
@bp.route('/releases/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def delete(id):
    g.db.call_procedure("DELETE_MUSIC_RELEASE", [id])

    rows = g.db.select_from_table('MUSIC_RELEASE')[0]

    return render_template("admin/Release/list.html", output=rows)
