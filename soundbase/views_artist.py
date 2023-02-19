from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import admin_login_required
from soundbase import db
import cx_Oracle
from soundbase.db import requires_db_connection

bp = Blueprint("views_artist", __name__)


@bp.route('/artists', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def artists():
    if request.method == 'POST':
        search = request.form['SearchString']
        if search.isDigit():
           rows = g.db.select_from_table("ARTIST",
                                         where_list=[{"ARTIST_ID":search},
                                                     {"%ARTIST_NAME":search})
        else:
           rows = g.db.select_from_table("ARTIST", where_list={"%ARTIST_NAME":search})
           
        return render_template("admin/Artist/list.html", output=rows)
    rows = g.db.select_from_table("ARTIST")[0]
    return render_template("admin/Artist/list.html", output=rows)


@bp.route('/artists/create', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
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
                g.db.call_procedure("ADD_ARTIST", [name, startdate, descr])
            else:
                flash(error)
        except Exception as ex:
            flash("{0} has occured!".format(type(ex).__name__))
    return render_template("admin/Artist/create.html")


@bp.route('/artists/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
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

            # Edit the artist via procedure
            if error is None:
                g.db.call_procedure("EDIT_ARTIST", [id, name, startdate, descr])
                flash('Artist edited successfully!')
            else:
                flash(error)
        except:
            flash('Date must be in format dd-mm-yyyy')

    rows, names = g.db.select_from_table("ARTIST", {"ARTIST_ID": id})
    userdata = list(rows[0])
    # Get date component of timestamp
    userdata[2] = str(userdata[names["ACTIVITY_START_DATE"]])[:str(userdata[names["ACTIVITY_START_DATE"]]).index(' ')]

    return render_template("admin/artist/edit.html", output=userdata)


@bp.route('/artists/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def delete(id):
    g.db.call_procedure("DELETE_ARTIST", id)
    rows, names = g.db.select_from_table("ARTIST")

    return render_template("admin/artist/list.html", output=rows)


@bp.route('/artists/details/<id>', methods=['GET', 'POST'])
@admin_login_required
@requires_db_connection
def details(id):
    rows, names = g.db.select_from_table("ARTIST", {"ARTIST_ID": id})
    userdata = rows[names["ARTIST_ID"]]
    return render_template("admin/Artist/details.html", output=userdata)
