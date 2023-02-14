from flask import Blueprint, render_template, request, flash
from soundbase.auth import login_required
import cx_Oracle

bp = Blueprint("views_artist", __name__)

@bp.route('/artists', methods=['GET', 'POST'])
@login_required
def artists():
    if request.method == 'POST':
        search = request.form['SearchString']

        conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
        cursor = conn.cursor()
        searchid=None
        if search.isdigit():
            searchid=search
        cursor.execute("SELECT * FROM ARTIST where artist_id = :x or artist_name like :y",x=searchid,y='%'+search+'%')
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/Artist/list.html", output=rows)
    #TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ARTIST")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Artist/list.html", output=rows)

@bp.route('/artists/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Get the artist data from the form
        name = request.form['name']
        startdate = request.form['date']
        descr = request.form['description']

        from datetime import date, datetime
        try:
            if startdate is not None and startdate != "":
                startdate = datetime.strptime(startdate, '%Y-%m-%d')
            error = None
            if not name:
                error = "Name is required."
            elif startdate is not None and startdate != '' and startdate.date() > date.today():
                error = "Date can't be from the future!"

            # Connect to the database and add the new artist
            if error is None:
                # DO ZMIANY POTEM
                conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
                cursor = conn.cursor()

                cursor.callproc('ADD_ARTIST', [name, startdate, descr])
                conn.commit()
                cursor.close()
                conn.close()
                flash('Artist added successfully!')
            else:
                flash(error)
        except:
            flash('Date must be in format dd-mm-yyyy')
    return render_template("admin/Artist/createSingle.html")

@bp.route('/artists/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        # Get the artist data from the form
        name = request.form['name']
        startdate = request.form['date']
        descr = request.form['description']

        from datetime import date, datetime

        try:
            if startdate is not None and startdate != "":
                startdate = datetime.strptime(startdate, '%Y-%m-%d')
            error = None
            if not name:
                error = "Name is required."
            elif startdate is not None and startdate != "" and startdate.date() > date.today():
                error = "Date can't be from the future!"

            # Connect to the database and edit the artist
            if error is None:
                #DO ZMIANY POTEM
                conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
                cursor = conn.cursor()


                cursor.callproc('EDIT_ARTIST', [id, name, startdate, descr])
                conn.commit()
                cursor.close()
                conn.close()
                flash('Artist edited successfully!')
            else:
                flash(error)
        except:
            flash('Date must be in format dd-mm-yyyy')


    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ARTIST WHERE ARTIST_ID = :id", id=id)

    userdata = list(cursor.fetchone())
    print(userdata[2])
    userdata[2] = str(userdata[2])[:str(userdata[2]).index(' ')]
    print(userdata[2])

    cursor.close()
    conn.close()
    return render_template("admin/Artist/edit.html", output = userdata)

@bp.route('/artists/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_ARTIST', [id])
    conn.commit()

    cursor.execute("SELECT * FROM ARTIST")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Artist/list.html", output=rows)

@bp.route('/artists/details/<id>', methods=['GET', 'POST'])
@login_required
def details(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ARTIST WHERE ARTIST_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/Artist/details.html", output = userdata)