import functools
from awokogbon.db import open_db
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)
from flask import (
  Blueprint,
  flash,
  g,
  redirect,
  render_template,
  request,
  session,
  url_for
)

blueprint = Blueprint('auth', __name__, url_prefix='/auth')  # initialize a Blueprint instance


def init_blueprint(app):  # registers `blueprint_instance`
    app.register_blueprint(blueprint)  # tells flask to register `bp` after creating the `app` instance


# Registeration Page View:
#   - show `form` as response
#   - parse `submitted` form data
#   - validate `submitted` form data
#   - handle error due to `submitted` form data
#   - return a new `submitted` form (i.e. register page) if `submitted data` is invalid
#   - else redirect to login page view
@blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = open_db()
        error = None

        if not username:  # if username is `None`, just throw an error
            error = 'Username is required.'
        elif not password:  # if password is `None`, also throw an error
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:  # use initialized db to check if user already exists
            error = 'User {} is already registered.'.format(username)

        if error is None:  # if there are no errors with username and password input, then hash and store the data in the database
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
            db.commit()  # make sure the db changes are concreted i.e. save the changes
            return redirect(url_for('auth.login'))   # redirect the user to `login` for them to now login

        flash(error)  # shows the user the error and also stores the error for subsequent usage in the template

    return render_template('auth/register.html')

# Login Page View:
#   - show `form` as response
#   - parse `submitted` form data
#   - validate `submitted` form data
#   - handle error due to `submitted` form data
#   - return a new form (i.e. same login page template), if `submitted data` is invalid
#   - else redirect to `index page` view
@blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = open_db()
        error = None

        # validate the user whether it exists or correct
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()  # get the user record from database

        if user is None:  # if username is `None`, just throw an error
            error = 'Incorrect username.'

        elif not check_password_hash(user['password'], password):  # validate by hashing new password and comparing with db version
            error = 'Incorrect password.'

        if error is None:  # username and password have been validated
            session.clear()  # clear the current session cookies
            session['user_id'] = user['id']  # add user to session dict - `id` is the unique identifier obtained from the database
            return redirect(url_for('index'))   # redirect the user to `index page`, after having logged in

        flash(error)  # shows the user the error and store the error

    return render_template('auth/login.html')  # otherwise return the login page again 


# Logged In User Page View:
#   - validate if user (with currently session cookie) is already logged in
#   - before even running other page views
@blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')  # extract the user_id from the current session cookie
    if user_id is None:  # if there current session cookie is not valid [due to not even having a user_id]
        g.user = None
    else:  # use the user_id to select the user details from the database
        db = open_db()
        g.user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


# Logged Out User Page View
#   - clear the session cookie - so as to remove the user_id from the session cookie
#   - return the user to the index page
@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Login Required Page View
#   - a decorator required to extend create/edit/delete posts page views
#   - so as to ensure that the user is logged in before they can create/edit/delete posts


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):  # what the new function actually does
        if g.user is None:  # if the user is not logged in yet [i.e. no user_id stored in `g.user`]
            return redirect(url_for('auth.login'))
        return view(**kwargs)  # returns the original view (e.g. edit post page) for the user to then continue (business as usual)
    return wrapped_view  # the new function that is returned
