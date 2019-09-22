# unit tests focused on the `application factory` create_app(test_config=None)

from awokogbon import create_app


def test_creat_app():
    assert not create_app().testing  # create_app() is an instance of Flask, with `testing` attribute that is `false` by default [when not config is passed]
    assert create_app({'TESTING': True}).testing  # now that config '{TESTING: True}' is passed, then `create_app().testing` should be `true`


def test_hello(client):  # `client` is automagically made available due to it being defined as a pytest fixtures
    response = client.get('/hello') # `client` is actually `flask.test_client` which has a `get` attribute
    assert response.data == b'Hello, World!'  # b'' converts the string into bytes, which is the datatype for `response.data`
