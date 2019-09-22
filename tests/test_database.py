# unit tests focused on the database connection handler
# it tests the open_db(), close_db(), init_db(), init_db_command() and init_app() functions

import sqlite3
import pytest

from awokogbon.db import open_db


# `app` is automatically available as an argument because we already defined it as a fixture in conftest.py
def test_close_db(app):  # to validate the app can be `opened` and `closed` () 
    with app.app_context():  # this gives access to the current_app [thus access to the attributes - within this block of code]
        db = open_db()  # extracts and assigns the `open_db()` obtained from the app_context()
        assert db is open_db()  # checks to make sure we were able to really get the same db object from app_context()

    with pytest.raises(sqlite3.ProgrammingError) as e:  # test if db.execute(`SELECT 1`) raises expected `sqlite3.ProgrammingError` or exception `e` [i.e. string `close`] 
        db.execute('SELECT 1')  # `SELECT 1` always returns a `1` if there are rows in the db [] - this also implicitly tests open_db()

    # the returned rows is unimportant, we just want to test if the code returns a `close` value
    assert 'close' in str(e.value)  # check that if string `close` exists to show that close_db() is working well


# `runner` is automatically available as an argument, because it is already defined in conftest.py
# monkeypatch is inherently available as a fixture internal to pytest
# helps us to TEMPORARILY `decorate` the `init_db()` function with a desired attribute e.g. Logger.
def test_init_db_command(runner, monkeypatch):
    class Logger(object):  # create the mocking class 
        flag = False

    def mock_flag():  # define the method to be used to upgrade the initial `init_db()` with an activity logger
        Logger.flag = True  # sets the flag to `True` whenever `mock_flgag()` is ran

    monkeypatch.setattr('awokogbon.db.init_db', mock_flag)
    result = runner.invoke(args=['init-db'])  # `runner` is instance of `test_cli_runner`, with `invoke()` method, that returns a `result object`
    assert 'Initialized' in result.output  # the `result` object has the `output` attribute: which gives the result as a `unicode string`
    assert Logger.flag  # this should be true, if `awokogbon.db.init_db()` was ran i.e. `awokogbon.db.init_db.mock_flag()` also runs implicitly
