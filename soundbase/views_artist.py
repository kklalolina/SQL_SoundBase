from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import admin_login_required
from soundbase import db
import cx_Oracle

bp = Blueprint("views_artist", __name__)


@bp.route('/artists', methods=['GET', 'POST'])
@admin_login_required
def artists():
    if request.method == 'POST':
        search = request.form['SearchString']
        rows = g.db.select_search_artist(search)
        return render_template("admin/Artist/list.html", output=rows)
    rows = g.db.select_from_table("ARTIST")
    return render_template("admin/Artist/list.html", output=rows)


@bp.route('/artists/create', methods=['GET', 'POST'])
@admin_login_required
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
                g.db.add_artist(name, startdate, descr)
            else:
                flash(error)
        except:
            flash('Date must be in format dd-mm-yyyy')
    return render_template("admin/Artist/createSingle.html")


@bp.route('/artists/edit/<id>', methods=['GET', 'POST'])
@admin_login_required
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
                g.db.edit_artist(id, name, startdate, descr)
                flash('Artist edited successfully!')
            else:
                flash(error)
        except:
            flash('Date must be in format dd-mm-yyyy')

    rows = g.db.select_from_table("ARTIST", {"ARTIST_ID": id})
    userdata = rows[0]
    # Get date component of timestamp
    userdata[2] = str(userdata[2])[:str(userdata[2]).index(' ')]

    return render_template("admin/Artist/edit.html", output=userdata)


@bp.route('/artists/delete/<id>', methods=['GET', 'POST'])
@admin_login_required
def delete(id):
    g.db.delete_artist(id)
    rows = g.db.select_from_table("ARTIST")

    return render_template("admin/Artist/list.html", output=rows)


@bp.route('/artists/details/<id>', methods=['GET', 'POST'])
@admin_login_required
def details(id):
    rows = g.db.select_from_table("ARTIST", {"ARTIST_ID": id})
    userdata = rows[0]
    return render_template("admin/Artist/details.html", output=userdata)
