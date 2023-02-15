from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import login_required, db, admin_login_required
import oracledb

bp = Blueprint("views", __name__)

@bp.route('/')
def index():
    try:
        g.db = db.Database()
    except oracledb.Error:
        # Error connection to database view
        # TODO: I'm thinking we might need to check the validity of the db connection before every view. Should I write
        # TODO: a decorator for that?
        print("Can't connect to database.")
        return
    finally:
        return render_template("user/index.html")


@bp.route('/admin')
@admin_login_required
def admin():
    return render_template("admin/index.html")
