from flask import Blueprint, render_template, request, flash
from soundbase.auth import admin_login_required
import cx_Oracle

bp = Blueprint("views_user", __name__)

# Should these be admin exclusive?
@bp.route('/users', methods=['GET', 'POST'])
@admin_login_required
def users():
    if request.method == 'POST':
        search = request.form['SearchString']
        print(search)
        conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
        cursor = conn.cursor()
        searchid=None
        searchtype=None
        if search.isdigit():
            searchid=search
        if search.capitalize().find('Admin')!=-1:
            searchtype=1
        if search.capitalize().find('Basic')!=-1:
            searchtype=0
        cursor.execute("SELECT * FROM SOUNDBASE_USERS where user_id = :x or username like :y or user_type like :z",x=searchid,y='%'+search+'%',z=searchtype)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/User/list.html", output=rows)
    #TESTOWE POLACZENIE Z BAZA POKI NIEZRIOBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SOUNDBASE_USERS")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/User/list.html", output=rows)

@bp.route('/create', methods=['GET', 'POST'])
@admin_login_required
def create():
    if request.method == 'POST':
        # Get the user data from the form
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']
        usr_type = request.form['usr_type']

        error = None
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif any(char.isspace() for char in username):
            error = "Username cant contain any whitespaces!"
        elif len(password)<8 or not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            error = "Password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif(password!=cpassword):
            error= "Passwords must match!"

        # Connect to the database and add the new user
        if error is None:

            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()
            cursor.callproc('ADD_USER', [username,password])
            conn.commit()
            cursor.close()
            conn.close()
            flash('User added successfully!')
        else:
            flash(error)
            print(error)
    return render_template("admin/User/create.html")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
def edit(id):
    if request.method == 'POST':
        # Get the user data from the form
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']

        error = None
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif len(password)<8 or not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            error = "Password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif password != cpassword:
            error= "Passwords must match!"

        # Connect to the database and edit the user
        if error is None:
            #DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
            cursor = conn.cursor()
            cursor.callproc('EDIT_USER', [id, username, password])
            conn.commit()
            cursor.close()
            conn.close()
            flash('User edited successfully!')
        else:
            flash(error)
            print(error)

    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SOUNDBASE_USERS WHERE USER_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/User/edit.html", output = userdata)

@bp.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()

    cursor.callproc('DELETE_USER', [id])
    conn.commit()

    cursor.execute("SELECT * FROM SOUNDBASE_USERS")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/User/list.html", output=rows)

@bp.route('/details/<id>', methods=['GET', 'POST'])
def details(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/Admin123@localhost:1522/sound")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SOUNDBASE_USERS WHERE USER_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/User/details.html", output = userdata)