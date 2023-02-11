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
