from flask import Blueprint, render_template, request, flash
from soundbase.auth import login_required
import cx_Oracle

bp = Blueprint("views", __name__)

@bp.route('/')
def index():
    return render_template("user/index.html")


@bp.route('/admin')
@login_required
def admin():
    return render_template("admin/index.html")
@bp.route('/users')
@login_required
def users():
    #TESTOWE POLACZENIE Z BAZA POKI NIEZRIOBIONE DB.PY
    conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/User/base.html", output=rows)

@bp.route('/createUser', methods=['GET', 'POST'])
def createUser():
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
        elif not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            error = "Password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif(password!=cpassword):
            error= "Passwords must match!"

        # Connect to the database and add the new user
        if error is None:
            # DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
            cursor = conn.cursor()
            cursor.callproc('ADD_USER', [username,'01-JAN-21', password, int(usr_type)])
            conn.commit()
            cursor.close()
            conn.close()
            flash('User added successfully!')
        else:
            flash(error)
            print(error)
    return render_template("admin/User/create.html")

@bp.route('/editUser/<id>', methods=['GET', 'POST'])
def editUser(id):
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
        elif not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            error = "Password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif password != cpassword:
            error= "Passwords must match!"

        # Connect to the database and edit the user
        if error is None:
            #DO ZMIANY POTEM
            conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
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
    conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE USER_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/User/edit.html", output = userdata)

@bp.route('/delete/<id>', methods=['GET', 'POST'])
def deleteUser(id): #do naprawy
    print("ID"+id)
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
    cursor = conn.cursor()

    cursor.callproc('DELETE_USER', [id])
    conn.commit()

    cursor.execute("SELECT * FROM USERS")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/User/base.html", output=rows)

@bp.route('/details/<id>', methods=['GET', 'POST'])
def detailsUser(id):
    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    conn = cx_Oracle.connect("system/HASLO@localhost:1522/NAZWABAZY")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE USER_ID = :id", id=id)

    userdata = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("admin/User/details.html", output = userdata)