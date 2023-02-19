import werkzeug.exceptions
from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import admin_login_required
from soundbase.db import requires_db_connection

bp = Blueprint("views_rating", __name__)


@bp.route('/ratings', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def ratings():
    if request.method == 'POST':
        search = request.form['SearchString']
        if not search.isdigit():  # we search only on digits, if not a digit then dont search coz sql will throw some errorrrr
            rows, names = g.db.select_from_table("RATING")
        else:
            rows, names = g.db.select_from_table("RATING", [{"RATING_ID": search}, {"SOUNDBASE_USERS_ID": search},
                                                            {"RATED_RELEASE_ID": search}, {"STAR_VALUE": search}])
        return render_template("admin/Rating/list.html", output=rows)
    rows, names = g.db.select_from_table("RATING")

    return render_template("admin/Rating/list.html", output=rows)


@bp.route('/ratings/create', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def create():
    if request.method == 'POST':
        star = request.form['star']
        try:
            release = request.form['release']
            user = request.form['user']
        except werkzeug.exceptions.BadRequestKeyError:
            flash("Please select the release/user by clicking on them!")
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
            g.db.call_procedure("ADD_RATING", [star, date, user, release, content])
            flash('Rating added successfully!')
        else:
            flash(error)
    user_rows = g.db.select_from_table("SOUNDBASE_USERS", select_list=["USER_ID", "USERNAME"])[0]
    release_rows = g.db.select_from_table("MUSIC_RELEASE", select_list=["RELEASE_ID", "RELEASE_NAME"])[0]

    if not release_rows:  # cant add rating if no releases or users
        flash("No releases in the database!")
        return ratings()
    elif not user_rows:
        flash("No users in the database!")
        return ratings()

    return render_template("admin/Rating/create.html", users=user_rows, releases=release_rows)


@bp.route('/ratings/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
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
            g.db.call_procedure('EDIT_RATING', [id, star, user, release, content])
            flash('Rating edited successfully!')
        else:
            flash(error)

    # TESTOWE POLACZENIE Z BAZA POKI NIEZROBIONE DB.PY
    rating_data = g.db.select_from_table("RATING", {"RATING_ID": id})[0][0]
    user_data = g.db.select_from_table("SOUNDBASE_USERS", select_list=["USER_ID", "USERNAME"])[0]
    release_data = g.db.select_from_table("MUSIC_RELEASE", select_list=["RELEASE_ID", "RELEASE_NAME"])[0]

    return render_template("admin/Rating/edit.html", output=rating_data, users=user_data, releases=release_data)


@bp.route('/ratings/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def delete(id):
    g.db.call_procedure("DELETE_RATING", [id])
    rows = g.db.select_from_table("RATING")[0]
    return render_template("admin/Rating/list.html", output=rows)


@bp.route('/ratings/details/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def details(id):
    rating_data, names = g.db.select_from_table("RATING", {"RATING_ID": id})
    rating_data = rating_data[0]

    username = g.db.select_from_table("SOUNDBASE_USERS",
                                      {"USER_ID": rating_data[names["SOUNDBASE_USERS_ID"]]},
                                      select_list=["USERNAME"])[0][0][0]

    release_name = g.db.select_from_table("MUSIC_RELEASE",
                                          {"RELEASE_ID": rating_data[names["RATED_RELEASE_ID"]]},
                                          select_list=["RELEASE_NAME"])[0][0][0]
    return render_template("admin/Rating/details.html", output=rating_data, username=username, releasename=release_name)
