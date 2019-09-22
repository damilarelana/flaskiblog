# Here testing setup functions are configured
import os
import tempfile
import pytest
from awokogbon import create_app
from awokogbon.db import open_db, init_db


# parse sql statement to be used to create testdata
# determine directory, concatenate to determine full file path
# open the files as `f` with modes of being `read-only` and `binary`
# save the file a private variable `data_sql` which cannot be imported from this module
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


# setup fixtures i.e. functions that manage test consumables (i.e. database connections, urls, data etc.)
# to ensure that local dev environ is not used for testing i.e. separates `test environment from `dev environment'
# implemented via decorators `@pytest.fixture`
# fixtures are not the actual test functions themselves


@pytest.fixture
def app():  # for the `testing of the application itself: awokogbon`
    db_tempfile, db_tempfilepath = tempfile.mkstemp()  # create temporary file/path needed for the tests database

    app = create_app({  # create an instance of the application
        'TESTING': True,  # let's flask know that the application is in testing mode
        'DATABASE': db_tempfilepath,  # points to the database path where `_data_sql` would be stored when used
    })

    with app.app_context():  # initialize the app context e.g. app `in testing mode` to use test database `_data_sql`
        init_db()  # gets the app to use initiliaze the sqlite3 connections [which also gets `schema.sql` initialized BUT not used]
        open_db().executescript(_data_sql)  # gets the app to open/run `_data_sql`, and initialize it as an `sqlite3 db` at `db_tempfilepath` [i.e. `schema.sql` is not used]

    yield app  # `an alternative to using return` i.e. a more efficient `return` [what works like a generator]

    # close the temporary file and unlink the temporary file path
    os.close(db_tempfile)
    os.unlink(db_tempfilepath)


# test actions which we do not want to repeat within test_authentication.py itself
# e.g. making of POST requests
class AuthenticationActions(object):
    def __init__(self, client):  # it takes a `client` object
        self._client = client  # prefix underscore helps to ensure that it is private and not imported by other packages

    def login(self, username='test', password='test'):
        return self._client.post(  # takes the same parameters like `EnvironBuilder` i.e. `path` (url), `data` (a dict payload of forms) etc.
            '/auth/login',  # we're not using url_for('auth.login') to avoid circular reasoning i.e. use of what we are testing `auth.py`
            data={'username': username, 'password': password}  # `key` values matches the table names
        )

    def logout(self):
        return self._client.get('/auth/logout')  # this is a simply get request to .logout() within app_context


# register the authentication actions [via the class] as fixtures
@pytest.fixture
def authentication(client):
    return AuthenticationActions(client)


@pytest.fixture
def client(app):  # for the `simulated client test meant to access the app, in order to test it`
    return app.test_client()


@pytest.fixture
def runner(app):  # for `simulate cli command runner` meant to run the Click commands registered with app
    return app.test_cli_runner()