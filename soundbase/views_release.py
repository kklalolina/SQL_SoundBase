
from flask import Blueprint, render_template, request, flash
from soundbase.auth import login_required
import cx_Oracle


bp = Blueprint("views_release", __name__)
# ---------------------------------------SINGLE------------------------------------------------------
@bp.route('/releases', methods=['GET', 'POST'])
@login_required
def releases():
    if request.method == 'POST':
        search = request.form['SearchString']
        conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
        cursor = conn.cursor()
        searchid=None
        if search.isdigit():
            searchid=search
        cursor.execute("SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID WHERE RELEASE_ID = :x OR RELEASE_NAME LIKE :y OR TYPE_NAME LIKE :y",x=searchid,y='%'+search+'%')

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/Release/list.html", output=rows)
    #TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT RELEASE_ID,RELEASE_NAME,RELEASE_DATE,t.TYPE_NAME FROM MUSIC_RELEASE m JOIN RELEASE_TYPE t ON m.RELEASE_TYPE_ID=t.TYPE_ID")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Release/list.html", output=rows)

@bp.route('/releases/createSingle', methods=['GET', 'POST'])
@login_required
def createSingle(): # po prostu wydanie z jedna piosenka - moze byc wiele artystow -----moze trzeba zmienic nazwe funkcji ale nie mam pomyslu
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
            error='Date must be in format dd-mm-yyyy'
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
            if int(hours)>23:
                days=str(int(hours)//24)
                hours=str(int(hours)%24)
            if int(hours) < 10:
                hours='0'+hours
            if int(minutes) < 10:
                minutes='0'+minutes
            if int(seconds) < 10:
                seconds='0'+seconds
            length = days+' '+hours+':'+minutes+':'+seconds



            # Connect to the database and add the new Release
            if error is None:
                # DO ZMIANY POTEM
                conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
                cursor = conn.cursor()

                cursor.callproc('ADD_TRACK', [trackname, length])

                # ZAPEWNIC ZEBY TYPE ISTNIAL!!!!
                cursor.execute("SELECT TYPE_ID FROM RELEASE_TYPE WHERE TYPE_NAME LIKE :x",x='Single')
                type_id = cursor.fetchone()[0]

                cursor.callproc('ADD_MUSIC_RELEASE',[name, releasedate, type_id])

                cursor.execute("SELECT RELEASE_ID FROM MUSIC_RELEASE WHERE RELEASE_NAME LIKE :x",x=name)
                release_id = cursor.fetchone()[0]
                cursor.execute("SELECT TRACK_ID FROM TRACK WHERE TRACK_NAME LIKE :x",x=trackname)
                track_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO TRACKS_IN_RELEASE (RELEASE_ID, TRACK_ID, TRACK_NO) VALUES (:release_id, :track_id, 1)",release_id=release_id, track_id=track_id)
                conn.commit()
                print(artists)
                for i in artists:
                    print(i)
                    cursor.execute("INSERT INTO ARTIST_OF_RELEASE (ARTIST_ID, RELEASE_ID) VALUES (:artist_id, :release_id)",release_id=release_id, artist_id=i)
                    conn.commit()
                cursor.execute("INSERT INTO GENRE_OF_RELEASE (GENRE_ID, RELEASE_ID) VALUES (:genre_id, :release_id)",release_id=release_id, genre_id=genre)
                conn.commit()
                cursor.execute("INSERT INTO TAG_OF_RELEASE (TAG_ID, RELEASE_ID) VALUES (:tag_id, :release_id)",release_id=release_id, tag_id=tag)
                conn.commit()

                conn.commit()
                cursor.close()
                conn.close()
                flash('Release added successfully!')
            else:
                flash(error)
        else:
            flash(error)

    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()


    cursor.execute("SELECT ARTIST_ID, ARTIST_NAME FROM ARTIST")
    artists = cursor.fetchall()

    cursor.execute("SELECT GENRE_ID, GENRE_NAME FROM GENRE")
    genres=cursor.fetchall()

    cursor.execute("SELECT TAG_ID, TAG_NAME FROM DESCRIPTIVE_TAG")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("admin/Release/createSingle.html", artists=artists, genres=genres, tags=tags)



@bp.route('/releases/details/<id>', methods=['GET', 'POST'])
@login_required
def detailsSingle(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM MUSIC_RELEASE WHERE RELEASE_ID = :id", id=id)
    release = cursor.fetchone()

    cursor.execute("SELECT TRACK_ID FROM TRACKS_IN_RELEASE WHERE RELEASE_ID = :id", id=id)
    track_id = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=int(track_id))
    track = cursor.fetchone()

    cursor.execute("SELECT ARTIST_ID FROM ARTIST_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    artists_id = cursor.fetchall()

    artists_id=[x[0] for x in artists_id]
    artists=[]

    for i in artists_id:
        cursor.execute("SELECT ARTIST_NAME FROM ARTIST WHERE ARTIST_ID = :id", id=i)
        artists.append(cursor.fetchone()[0])

    cursor.execute("SELECT GENRE_ID FROM GENRE_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    genre_id = cursor.fetchone()[0]
    cursor.execute("SELECT GENRE_NAME FROM GENRE WHERE GENRE_ID = :id", id=genre_id)
    genre = cursor.fetchone()[0]

    cursor.execute("SELECT TAG_ID FROM TAG_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    tag_id = cursor.fetchone()[0]
    cursor.execute("SELECT TAG_NAME FROM DESCRIPTIVE_TAG WHERE TAG_ID = :id", id=tag_id)
    tag = cursor.fetchone()[0]

    cursor.execute("SELECT TYPE_NAME FROM RELEASE_TYPE WHERE TYPE_ID = :id", id=release[3])
    type_name = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template("admin/Release/detailsSingle.html", release = release, genre = genre, artists = artists,track = track,type=type_name, tag=tag)


#------------------------------------------ALBUM---------------------------------------------------

@bp.route('/releases/createAlbum', methods=['GET', 'POST'])
@login_required
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
            error='Date must be in format dd-mm-yyyy'
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
                # DO ZMIANY POTEM
                conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
                cursor = conn.cursor()



                # ZAPEWNIC ZEBY TYPE ISTNIAL!!!!
                cursor.execute("SELECT TYPE_ID FROM RELEASE_TYPE WHERE TYPE_NAME LIKE :x",x='Album')
                type_id = cursor.fetchone()[0]

                cursor.callproc('ADD_MUSIC_RELEASE',[name, releasedate, type_id])

                cursor.execute("SELECT RELEASE_ID FROM MUSIC_RELEASE WHERE RELEASE_NAME LIKE :x",x=name)
                release_id = cursor.fetchone()[0]

                for i in artists:
                    cursor.execute("INSERT INTO ARTIST_OF_RELEASE (ARTIST_ID, RELEASE_ID) VALUES (:artist_id, :release_id)",release_id=release_id, artist_id=i)
                    conn.commit()
                cursor.execute("INSERT INTO GENRE_OF_RELEASE (GENRE_ID, RELEASE_ID) VALUES (:genre_id, :release_id)",release_id=release_id, genre_id=genre)
                conn.commit()
                cursor.execute("INSERT INTO TAG_OF_RELEASE (TAG_ID, RELEASE_ID) VALUES (:tag_id, :release_id)",release_id=release_id, tag_id=tag)
                conn.commit()

                conn.commit()
                cursor.close()
                conn.close()
                flash('Release added successfully!')
            else:
                flash(error)
        else:
            flash(error)

    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()


    cursor.execute("SELECT ARTIST_ID, ARTIST_NAME FROM ARTIST")
    artists = cursor.fetchall()

    cursor.execute("SELECT GENRE_ID, GENRE_NAME FROM GENRE")
    genres=cursor.fetchall()

    cursor.execute("SELECT TAG_ID, TAG_NAME FROM DESCRIPTIVE_TAG")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("admin/Release/createAlbum.html", artists=artists, genres=genres,tags=tags)

@bp.route('/releases/<id>/addTrack', methods=['GET', 'POST'])
@login_required
def addTrack(id):
    if request.method == 'POST':
        # Get the tracks data from the form
        name = request.form['name']
        hours = str(request.form['hours'])
        minutes = str(request.form['minutes'])
        seconds = str(request.form['seconds'])
        # Formatting the track length to sql interval format
        days = '0'
        if int(hours)>23:
            days=str(int(hours)//24)
            hours=str(int(hours)%24)
        if int(hours) < 10:
            hours='0'+hours
        if int(minutes) < 10:
            minutes='0'+minutes
        if int(seconds) < 10:
            seconds='0'+seconds
        length = days+' '+hours+':'+minutes+':'+seconds

        error = None
        if not name:
            error = "Name is required."

        # Connect to the database and add the new Track
        if error is None:
            # DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()

            cursor.callproc('ADD_TRACK', [name, length])
            conn.commit()

            cursor.execute("SELECT TRACK_ID FROM TRACK WHERE TRACK_NAME LIKE :x", x=name)
            track_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO TRACKS_IN_RELEASE (RELEASE_ID, TRACK_ID, TRACK_NO) VALUES (:release_id, :track_id, 1)",
                release_id=id, track_id=track_id)
            conn.commit()
            cursor.close()
            conn.close()
            flash('Track added successfully!')
        else:
            flash(error)

    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT RELEASE_NAME FROM MUSIC_RELEASE WHERE RELEASE_ID LIKE :x", x=id)
    releasename = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template("admin/Release/addTrack.html",releasename=releasename)

@bp.route('/releases/album/<id>/details', methods=['GET', 'POST'])
@login_required
def detailsAlbum(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM MUSIC_RELEASE WHERE RELEASE_ID = :id", id=id)
    release = cursor.fetchone()

    cursor.execute("SELECT TRACK_ID FROM TRACKS_IN_RELEASE WHERE RELEASE_ID = :id", id=id)
    tracks_id = cursor.fetchall()

    tracks_id = [x[0] for x in tracks_id]
    tracks = []

    for i in tracks_id:
        cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=i)
        tracks.append(cursor.fetchone())
    print(tracks)

    cursor.execute("SELECT ARTIST_ID FROM ARTIST_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    artists_id = cursor.fetchall()

    artists_id=[x[0] for x in artists_id]
    artists=[]

    for i in artists_id:
        cursor.execute("SELECT ARTIST_NAME FROM ARTIST WHERE ARTIST_ID = :id", id=i)
        artists.append(cursor.fetchone()[0])

    cursor.execute("SELECT GENRE_ID FROM GENRE_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    genre_id = cursor.fetchone()[0]
    cursor.execute("SELECT GENRE_NAME FROM GENRE WHERE GENRE_ID = :id", id=genre_id)
    genre = cursor.fetchone()[0]

    cursor.execute("SELECT TAG_ID FROM TAG_OF_RELEASE WHERE RELEASE_ID = :id", id=id)
    tag_id = cursor.fetchone()[0]
    cursor.execute("SELECT TAG_NAME FROM DESCRIPTIVE_TAG WHERE TAG_ID = :id", id=tag_id)
    tag = cursor.fetchone()[0]

    cursor.execute("SELECT TYPE_NAME FROM RELEASE_TYPE WHERE TYPE_ID = :id", id=release[3])
    type_name = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template("admin/Release/detailsAlbum.html", release = release, genre = genre, artists = artists,tracks = tracks,type=type_name,tag=tag)
@bp.route('/releases/album/<idr>/delete/<id>', methods=['GET', 'POST'])
@login_required
def deleteTrack(id,idr):
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_TRACK', [id])
    conn.commit()

    cursor.execute("SELECT * FROM MUSIC_RELEASE WHERE RELEASE_ID = :id", id=idr)
    release = cursor.fetchone()

    cursor.execute("SELECT TRACK_ID FROM TRACKS_IN_RELEASE WHERE RELEASE_ID = :id", id=idr)
    tracks_id = cursor.fetchall()

    tracks_id = [x[0] for x in tracks_id]
    tracks = []

    for i in tracks_id:
        cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=i)
        tracks.append(cursor.fetchone())
    print(tracks)

    cursor.execute("SELECT ARTIST_ID FROM ARTIST_OF_RELEASE WHERE RELEASE_ID = :id", id=idr)
    artists_id = cursor.fetchall()

    artists_id = [x[0] for x in artists_id]
    artists = []

    for i in artists_id:
        cursor.execute("SELECT ARTIST_NAME FROM ARTIST WHERE ARTIST_ID = :id", id=i)
        artists.append(cursor.fetchone()[0])

    cursor.execute("SELECT GENRE_ID FROM GENRE_OF_RELEASE WHERE RELEASE_ID = :id", id=idr)
    genre_id = cursor.fetchone()[0]
    cursor.execute("SELECT GENRE_NAME FROM GENRE WHERE GENRE_ID = :id", id=genre_id)
    genre = cursor.fetchone()[0]

    cursor.execute("SELECT TYPE_NAME FROM RELEASE_TYPE WHERE TYPE_ID = :id", id=release[3])
    type_name = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template("admin/Release/detailsAlbum.html", release=release, genre=genre, artists=artists,tracks=tracks, type=type_name)

#-----------------------delete any release------------
@bp.route('/releases/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_MUSIC_RELEASE', [id])
    conn.commit()

    cursor.execute("SELECT * FROM MUSIC_RELEASE")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Release/list.html", output=rows)