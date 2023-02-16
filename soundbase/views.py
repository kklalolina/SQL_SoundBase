from flask import Blueprint, render_template, request, flash, g
from soundbase.auth import login_required, admin_login_required
from soundbase.db import requires_db_connection
import oracledb

bp = Blueprint("views", __name__)

@bp.route('/')
def index():
    return render_template("user/index.html")


@bp.route('/admin')
@admin_login_required
@requires_db_connection
def admin():
    return render_template("admin/index.html")
