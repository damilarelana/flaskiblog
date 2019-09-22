# unit tests focused on blog post handler `blog.py`
# - tests `index()` view
# - tests `create()` view
# - tests `get_post()` view
# - tests `update()` view
# - tests `delete()` view

import pytest
from awokogbon.db import open_db


def test_index(client, authentication):

    # check to ensure user can access into the landing page [BEFORE log in]
    response = client.get('/')

    # test the kind of content they see while on the expected landing page, BEFORE log in
    assert b'Log In' in response.data
    assert b'Register' in response.data

    # test whether they can login, using the authenticationactions fixture
    authentication.login()

    # test the kind of content they see after they log in
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):  # this tests if `auth.login_required()` always redirects users to `url_for('auth.login')` [when attempting to access CUD views]
    response = client.post(path)
    assert response.headers.get('Location') == 'http://localhost/auth/login'


# tests to ensure correct user is logged in for  the current page view
# logged in user should not be able to modify another user's post
# - get current app.context
# - set ownership of current post to another user
# - not try to use the current app context to view the update/delete url for the updated post
# - server should throw a forbiden error 403 if we attempt to access a post with a wrong user
# - server should throw a not found 404 error if we attempt to access a post that does not even exist


# check logged_in_user if the server throws a forbiden error 403 if we attempt to access a post id = 1, now owned by anothe user_id = 2
@pytest.mark.parametrize('path', (
    '/1/update',
    '/1/delete',
))
def test_logged_in_user(app, client, authentication, path):

    # change the post owner within the test database
    with app.app_context():
        db = open_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    # ensure current user is logged in and then try to access the `/1/update` and `/1/delete` urls
    authentication.login()

    # test the routes
    assert client.post(path).status_code == 403  # forbidden

    # test visibility to edit link
    response = client.get('/')
    assert b'href="/1/update"' not in response.data


# checking if the server throws a 404 error if we attempt to access a post id=2 that does not even exist
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/update'
))
def test_exists_required(client, authentication, path):
    authentication.login()  # login with current user
    assert client.post(path).status_code == 404  # check if the user can access post_id 2 [for update/delete]


# test to ensure create() can
#  - access `/create` with a 200 status
#  - add new data into the data i.e. without having to use insert [but by leveraging the function behind `/create`]
def test_create(client, authentication, app):
    authentication.login()

    # tests to check if `/create` is accesssible
    assert client.get('/create').status_code == 200

    # add new data via the `/create` endpoint
    client.post(
        '/create',
        data={'title': 'created', 'body': ''}
    )

    # check if the data was indeed added
    # assuming that we initially had only one entry in the table `post`
    with app.app_context():
        db = open_db()
        count = db.execute(
            'SELECT COUNT(id) FROM post'
        ).fetchone()[0]
        assert count == 2


# test to ensure update() can
#  - access `/1/update` with a 200 status
#  - modify the data in an existing entry i.e. without having to use UPDATE [but by leveraging the function behind `/1/update`]
def test_update(client, authentication, app):
    authentication.login()

    # tests to check if `/1/update` is accesssible
    assert client.get('/1/update').status_code == 200

    # update new data via the `/1/update` endpoint
    client.post(
        '/1/update',
        data={'title': 'updated', 'body': ''}
    )

    # check if the data was indeed added by checking the title
    # assuming that we initially had only one entry in the table `post`
    # app.app_context is being used to simulate that the application code is the one implementing the test
    with app.app_context():
        db = open_db()
        post = db.execute(
            'SELECT  * FROM post WHERE id = 1'
        ).fetchone()
        assert post['title'] == 'updated'


# checking if both would show an error message with invalid data is used [which they should show]
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, authentication, path):
    authentication.login()

    # attempt to create/update invalid data i.e. empty field which is not allowed [based on table definition]
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


# test to ensure delete()
# - can reach the `/1/delete` endpoint
# - deletes the data from the database via the endpoint
# - shows that the data has indeed been deleted
# - shows that there was redirection back to blog.index.html
# - there is not specific test to check status 200 for a `/1/delete` view, because it does not have a dedicated template, rather it' been combined with update.html
def test_delete(client, authentication, app):
    authentication.login()

    # delete the post
    client.post('/1/delete')
    # response = client.post('/1/delete')

    # check to see if there was indeed redirection to `/` i.e. local host
    # assert response.headers.get('Location') == 'http://localhost/'

    # check if the data was indeed removed by checking the title
    # assuming that we initially had only one entry in the table `post`
    # app.app_context is being used to simulate that the application code is the one implementing the test
    with app.app_context():
        db = open_db()
        post = db.execute(
            'SELECT  * FROM post WHERE id = 1'
        ).fetchone()
        assert post is None
