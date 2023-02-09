import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

#from soundbase.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=('GET', 'POST'))
def register(): #----NA RAZIE NIE UZYWA BAZY DANYCH!! TYLKO SPRAWDZA POPRAWNOSC WYPELNIENIA FORMULARZA-----
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        '''if error is None:
            try:
                db.execute(
                    "INSERT INTO USERS (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered. Please select a different username or log in instead."
            else:
                return redirect(url_for("auth.login"))'''

        flash(error)

    return render_template('auth/signup.html')


@bp.route('/login', methods=('GET', 'POST'))
def login(): #----NA RAZIE LOGOWANIE NIE UZYWA BAZY DANYCH!! MOZNA SIE ZALOGOWAC JAKO:
    # admin haslo:admin, lub zwykly uzytkownik test haslo: test ------------
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if username == 'admin': #----OD TEGO MOMENTU WSZYSTKO DO PRZEROBIENIA KIEDY JUZ BEDZIE POLACZENIE Z BAZA--
            user = (0, username, password)
            if password != 'admin':
                error = 'Incorrect password.'
        elif username != 'test':
            error = 'Incorrect username.'
        else:
            if password != 'test':
                error = 'Incorrect password.'
        print(error)
        user = (1, username, password)
        print(user)
        '''db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM USERS WHERE USERNAME = ?', (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.' 
        '''
        if error is None:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['password'] = user[2]
            if session['username'] == 'admin':
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
        g.user = (user_id, session.get('username'), session.get('password'))


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


