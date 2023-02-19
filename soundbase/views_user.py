from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import admin_login_required
from oracledb import exceptions
from soundbase.db import requires_db_connection

bp = Blueprint("views_user", __name__)

# Should these be admin exclusive?
@bp.route('/users', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def users():
    if request.method == 'POST':
        search = request.form['SearchString']
        print(search)
        searchid = None
        searchtype = None
        if search.isdigit():
            searchid = search
        if search.capitalize().find('Admin') != -1:
            searchtype = 1
        if search.capitalize().find('Basic') != -1:
            searchtype = 0
        rows = g.db.select_from_table("SOUNDBASE_USERS",
                                      where_list=[{"USER_ID": searchid},
                                                  {"%USERNAME": search},
                                                  {"%USER_TYPE": searchtype}])[0]

        return render_template("admin/User/list.html", output=rows)
    rows = g.db.select_from_table("SOUNDBASE_USERS")[0]

    return render_template("admin/User/list.html", output=rows)

@bp.route('/create', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
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
        elif len(password)<8 or not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            error = "Password must contain at least 8 characters, at least one small letter, one big letter and one digit!"
        elif any(char.isspace() for char in username):
            error = "Username cannot contain any whitespaces!"
        elif password != cpassword:
            error= "Passwords must match!"

        # Connect to the database and add the new user
        if error is None:
            # DO ZMIANY POTEM
            try:
                g.db.call_procedure("ADD_USER", [username, password])
            except exceptions.IntegrityError:
                flash("Username already taken!")
            else:
                flash('User added successfully!')
        else:
            flash(error)
            print(error)
    return render_template("admin/User/create.html")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
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
        elif any(char.isspace() for char in username):
            error = "Username cannot contain any whitespaces!"
        elif password != cpassword:
            error= "Passwords must match!"


        # Connect to the database and edit the user
        if error is None:
            #DO ZMIANY POTEM
            g.db.call_procedure('EDIT_USER', [id, username, password])
            flash('User edited successfully!')
        else:
            flash(error)
    userdata = g.db.select_from_table("SOUNDBASE_USERS",
                           where_list={"USER_ID": id})[0][0]

    return render_template("admin/User/edit.html", output = userdata)

@bp.route('/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def delete(id):
    g.db.call_procedure('DELETE_USER', [id])

    rows = g.db.select_from_table("SOUNDBASE_USERS")[0]

    return render_template("admin/User/list.html", output=rows)

@bp.route('/details/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def details(id):
    userdata = g.db.select_from_table("SOUNDBASE_USERS",
                                      where_list={"USER_ID": id})[0][0]
    return render_template("admin/User/details.html", output=userdata)