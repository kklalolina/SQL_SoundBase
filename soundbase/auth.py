import functools

import soundbase.db_constants as db_constants
import oracledb
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, app
)
from soundbase.db import requires_db_connection
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=('GET', 'POST'))
@requires_db_connection
def register():  # ----NA RAZIE NIE UZYWA BAZY DANYCH!! TYLKO SPRAWDZA POPRAWNOSC WYPELNIENIA FORMULARZA-----
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        # Leave this alone for now
        if not username:
            error = "Username is required."
        elif any(char.isspace() for char in username):
            error = "Username cannot contain any whitespaces!"
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                g.db.call_proc("ADD_USER", [username, password])
            except oracledb.IntegrityError:
                error = "Username already taken."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/signup.html')


@bp.route('/login', methods=('GET', 'POST'))
@requires_db_connection
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        rows, names = g.db.select_from_table("SOUNDBASE_USERS", {"USERNAME": username})
        if not rows:
            error = "Incorrect username."
        else:
            user = rows[0]
            if not user[names['PASSWORD']] == password:
                error = "Incorrect password."

        if error is None:
            session.clear()
            session['user_id'] = user[names['USER_ID']]
            session['username'] = user[names['USERNAME']]
            session['password'] = user[names['PASSWORD']]
            session['type'] = user[names['USER_TYPE']]
            if session['type'] == db_constants.ADMIN_TYPE:
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
        if g.user is None or g.user[3] == db_constants.NORMAL_TYPE:
            # TODO: View for informing they're lacking certain permissions
            return redirect(url_for('views.index'))

        return view(**kwargs)

    return wrapped_view
