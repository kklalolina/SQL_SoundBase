
from flask import Blueprint, render_template, request, flash
from soundbase.auth import login_required
import cx_Oracle


bp = Blueprint("views_release", __name__)

@bp.route('/releases')
@login_required
def releases():
    #TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MUSIC_RELEASE")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Release/list.html", output=rows)

@bp.route('/releases/createSingle', methods=['GET', 'POST'])
@login_required
def createSingle():
    if request.method == 'POST':
        # Get the tracks data from the form

        artists = request.form.getlist('artists')
        name = request.form['name']
        releasedate = request.form['date']

        genre = request.form['genre']

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
                for i in artists:
                    cursor.execute("INSERT INTO ARTIST_OF_RELEASE (ARTIST_ID, RELEASE_ID) VALUES (:artist_id, :release_id)",release_id=release_id, artist_id=i)
                    conn.commit()
                cursor.execute("INSERT INTO GENRE_OF_RELEASE (GENRE_ID, RELEASE_ID) VALUES (:genre_id, :release_id)",release_id=release_id, genre_id=genre)
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

    cursor.close()
    conn.close()
    return render_template("admin/Release/create.html", artists=artists, genres=genres)

@bp.route('/releases/editSingle/<id>', methods=['GET', 'POST'])
@login_required
def editSingle(id): #todo
    if request.method == 'POST':
        # Get the Track data from the form
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

        # Connect to the database and edit the Track
        if error is None:
            #DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()


            cursor.callproc('EDIT_TRACK', [id, name, length])
            conn.commit()
            cursor.close()
            conn.close()
            flash('Track edited successfully!')
        else:
            flash(error)


    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=id)

    userdata = cursor.fetchone()

    data = [str(userdata[0]), str(userdata[1])] # [track_id, track_name]

    # Get hours, minutes and seconds from sql interval
    if str(userdata[2]).find('day') == -1: # if userdata[2] like '1:01:01'
        temp = str(userdata[2]).split(':')
        for i in temp:
            data.append(int(i))
    else: # if userdata[2] like '1 day 1:01:01'
        temp = str(userdata[2]).split()
        days = int(temp[0])
        temp = temp[-1]
        temp = temp.split(':')
        temp[0] = str(int(temp[0])+24*days)
        for i in temp:
            data.append(int(i))
    cursor.close()
    conn.close()
    return render_template("admin/Release/edit.html", output = data)

@bp.route('/releases/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_TRACK', [id])
    conn.commit()

    cursor.execute("SELECT * FROM TRACK")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Release/list.html", output=rows)

@bp.route('/releases/details/<id>', methods=['GET', 'POST'])
@login_required
def detailsSingle(id): #TODO
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM MUSIC_RELEASE WHERE RELEASE_ID = :id", id=id)
    release = cursor.fetchone()

    cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=id)
    track = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/Release/details.html", release = release, genre = None, artists = None,track = track)