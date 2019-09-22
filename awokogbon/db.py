import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def open_db():  # open_db() handles connection to the Sqlite [to setup a db pool to use]
    if 'db' not in g:  # is a flask special object used to pool db connections
        g.db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)  # handles connection to database specified by `current_app.config`
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):  # close_db() checks existing db connections and subsquently closing them checks if db connection exists and then closes it
    db = g.pop('db', None)  # pop (i.e. remove) the db connection from the exist stack (i.e. of db connections)

    if db is not None:
        db.close()


def init_db():  # init-db() initializes the SQL commands in schema.sql
    db = open_db()
    with current_app.open_resource('schema.sql') as f:  # the `open_resource()` method on current app instance opens a file relative to location of flaskr
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')  # a decorator to turn `init_db()`into a command line tool 
@with_appcontext  # this ensures application context is set when `init_db_command` is called
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):  # registers `init_db_command()` and `close_db()` to ensure application context. Both would be added to the application factory __init__.py
    app.teardown_appcontext(close_db)  # tells flask to use `close_db()` when tearing down db connections after returning a response
    app.cli.add_command(init_db_command)  # tells flask that `init-db` (i.e. `init_db_command`) can be run with flask command [within app context]
