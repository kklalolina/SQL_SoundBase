from flask import Blueprint, render_template, request, flash
from soundbase.auth import admin_login_required
import cx_Oracle



bp = Blueprint("views_track", __name__)

@bp.route('/tracks')
@admin_login_required
def tracks():
    #TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TRACK")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Track/list.html", output=rows)

@bp.route('/tracks/create', methods=['GET', 'POST'])
@admin_login_required
def create():
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
            cursor.close()
            conn.close()
            flash('Track added successfully!')
        else:
            flash(error)
    return render_template("admin/Track/createSingle.html")

@bp.route('/tracks/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
def edit(id):
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
    return render_template("admin/Track/edit.html", output = data)

@bp.route('/tracks/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
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

    return render_template("admin/Track/list.html", output=rows)

@bp.route('/tracks/details/<id>', methods=['GET', 'POST'])
@admin_login_required
def details(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TRACK WHERE TRACK_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/Track/detailsSingle.html", output = userdata)