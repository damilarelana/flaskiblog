# unit tests focused on user authentication handler `auth.py`
import pytest
from flask import g, session
from awokogbon.db import open_db


# test the register endpoint
def test_register(client, app):  # the `client` and `app` are feed to this via `conftest.py`
    # check if the '/auth/register' url is a accessible
    assert client.get('/auth/register').status_code == 200

    # use the validated url `/auth/register` to register a sample user `a`, using a post request
    response = client.post(
        '/auth/register',
        data={'username': 'a', 'password': 'a'}
    )

    # a successful registeration would re-direct the url to `url_for('auth.login')`, hence the `Location` check
    assert 'http://localhost/auth/login' == response.headers['Location']

    # check the database to ensure the data was really inserted for username `a`
    with app.app_context():
        db = open_db()
        assert db.execute(
            "select * from user where username = 'a'"
        ).fetchone() is not None


# tests the differennt registeration input `valiation error` scenarios
# error = 'Username is required.'
# error = 'Password is required'
# error = 'User {} is already registered.'.format(username)
@pytest.mark.parametrize(('username', 'password', 'renderedmessage'), (
    ('', '', b'Username is required.'),  # `no username` provided
    ('a', '', b'Password is required.'),  # `no password` provided
    ('test', 'test', b'already registered.'),
))
def test_register_input_validation(client, username, password, renderedmessage):
    response = client.post(  # call the registeration page
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert renderedmessage in response.data  # validate if the correct error message data is found in the rendered page data


# test the login endpoint
# using both the `client` and `authentication` fixtures
def test_login(client, authentication):
    # check if the '/auth/login' url is a accessible
    assert client.get('/auth/login').status_code == 200

    # authentication.login()
    response = authentication.login()
    assert response.headers.get('Location') == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


# tests the differennt login input validation scenarios
# error = 'Incorrect username'
# error = 'Incorrect password'
@pytest.mark.parametrize(('username', 'password', 'renderedmessage'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
    ))
def test_login_input_validation(authentication, username, password, renderedmessage):
    response = authentication.login(username, password)
    assert renderedmessage in response.data  # validate if the correct error message data is found in the rendered page data


# test the logout endpoint
def test_logout(client, authentication):
    authentication.login()

    with client:
        authentication.logout()
        assert 'user_id' not in session
