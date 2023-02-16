import functools

import cx_Oracle
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from soundbase import db

NORMAL_TYPE = 0
ADMIN_TYPE = 1
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=('GET', 'POST'))
def register():  # ----NA RAZIE NIE UZYWA BAZY DANYCH!! TYLKO SPRAWDZA POPRAWNOSC WYPELNIENIA FORMULARZA-----
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                g.db.add_users(username, password)
            except cx_Oracle.IntegrityError:
                error = "Username already taken."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/signup.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = g.db.select_from_table("SOUNDBASE_USERS", {"USERNAME": username})[0]

        if user is None:
            error = "Incorrect username."
        elif not user['PASSWORD'] == password:
            error = "Incorrect password."

        if error is None:
            session.clear()
            session['user_id'] = user['USER_ID']
            session['username'] = user['USERNAME']
            session['password'] = user['PASSWORD']
            session['type'] = user['USER_TYPE']
            if session['type'] == ADMIN_TYPE:
                return redirect(url_for('views.admin'))
            else:
                return redirect(url_for('views.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (user_id, session.get('username'), session.get('password'), session.get('type'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user[3] == NORMAL_TYPE: # none jest wtedy jak uzytkownik nie jest zalogowany
            # TODO: View for informing they're lacking certain permissions
            return redirect(url_for('views.index'))

        return view(**kwargs)

    return wrapped_view
