from flask import Blueprint, render_template, request, flash
from soundbase.auth import admin_login_required
import cx_Oracle



bp = Blueprint("views_rating", __name__)

@bp.route('/ratings', methods=['GET', 'POST'])
@admin_login_required
def ratings():
    if request.method == 'POST':
        search = request.form['SearchString']

        conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
        cursor = conn.cursor()
        if not search.isdigit(): # we search only on digits, if not a digit then dont search coz sql will throw some errorrrr
            cursor.execute("SELECT * FROM RATING")
        else:
            cursor.execute("SELECT * FROM RATING where rating_id = :x or SOUNDBASE_user_id = :x or RATED_release_id = :x or star_value = :x",x=search)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/Rating/list.html", output=rows)
    #TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RATING")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Rating/list.html", output=rows)

@bp.route('/ratings/create', methods=['GET', 'POST'])
@admin_login_required
def create():
    if request.method == 'POST':
        star = request.form['star']
        user = request.form['user']
        release = request.form['release']
        content = request.form['content']

        from datetime import date, datetime

        today = date.today()
        date = datetime.strptime(str(today), '%Y-%m-%d')
        error = None
        if not user:
            error = "User is required."
        elif not release:
            release = "Release is required."

        # Connect to the database and add the new rating
        if error is None:
            # DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()

            cursor.callproc('ADD_RATING', [star, date, user, release, content])
            conn.commit()
            cursor.close()
            conn.close()
            flash('Rating added successfully!')
        else:
            flash(error)
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT USER_ID,USERNAME FROM SOUNDBASE_USERS")

    users = cursor.fetchall()

    cursor.execute("SELECT RELEASE_ID,RELEASE_NAME FROM MUSIC_RELEASE")

    releases = cursor.fetchall()

    cursor.close()
    conn.close()

    if not releases: # cant add rating if no releases or users
        flash("No releases in the database!")
        return ratings()
    elif not users:
        flash("No users in the database!")
        return ratings()

    return render_template("admin/Rating/create.html", users=users, releases=releases)

@bp.route('/ratings/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
def edit(id):
    if request.method == 'POST':
        star = request.form['star']
        user = request.form['user']
        release = request.form['release']
        content = request.form['content']


        error = None
        if not user:
            error = "User is required."
        elif not release:
            release = "Release is required."

        # Connect to the database and add the new rating
        if error is None:
            # DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()

            cursor.callproc('EDIT_RATING', [id, star, user, release, content])
            conn.commit()

            cursor.close()
            conn.close()
            flash('Rating edited successfully!')
        else:
            flash(error)


    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RATING WHERE RATING_ID = :id", id=id)

    data = cursor.fetchone()

    cursor.execute("SELECT USER_ID,USERNAME FROM SOUNDBASE_USERS")

    users = cursor.fetchall()

    cursor.execute("SELECT RELEASE_ID,RELEASE_NAME FROM MUSIC_RELEASE")

    releases = cursor.fetchall()


    cursor.close()
    conn.close()
    return render_template("admin/Rating/edit.html", output = data, users=users, releases=releases)

@bp.route('/ratings/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
def delete(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_RATING', [id])
    conn.commit()

    cursor.execute("SELECT * FROM RATING")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/Rating/list.html", output=rows)

@bp.route('/ratings/details/<id>', methods=['GET', 'POST'])
@admin_login_required
def details(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM RATING WHERE RATING_ID = :id", id=id)
    data = cursor.fetchone()

    cursor.execute("SELECT USERNAME FROM SOUNDBASE_USERS WHERE USER_ID = :id", id=data[3])
    username = cursor.fetchone()[0]

    cursor.execute("SELECT RELEASE_NAME FROM MUSIC_RELEASE WHERE RELEASE_ID = :id", id=data[4])
    releasename = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template("admin/Rating/details.html", output = data, username=username, releasename=releasename)