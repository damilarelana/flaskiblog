from awokogbon.db import open_db
from awokogbon.auth import login_required
from werkzeug.exceptions import abort
from flask import (
  Blueprint,
  flash,
  g,
  redirect,
  render_template,
  request,
  url_for
)

blueprint = Blueprint('blog', __name__)  # initialize a Blueprint instance


def init_blueprint(app):  # registers `blueprint_instance` and then added to application factory __init__.py
    app.register_blueprint(blueprint)  # tells flask to register `bp` after creating `app` instance
    app.add_url_rule('/', endpoint='index')  # specifies the endpoint to point to e.g. `blog.index` and `/` would be the same


# Index Page View:
#   - just renders the exists blog posts
@blueprint.route('/')
def index():
    db = open_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON author_id = u.id'
        ' ORDER BY created DESC').fetchall()  # query and fetch all
    return render_template('blog/index.html', posts=posts)


# Create Post Page view
@blueprint.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:  # the blog post needs to have a title, assign an error value
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = open_db()
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)', (title, body, g.user['id'])
            )
            db.commit()  # save the data in the database
            return redirect(url_for('blog.index'))  # redirect back to index page after creating the new blog post
    return render_template('blog/create.html')  # redirect back to the create page if it is a `GET` request or there are issues with `title`


# middleware: required by update/delete handlers to which `post` to delete [for which `author`]
def get_post(id, check_author=True):

    # connect to the database to retrieve the post [using the provided `id` parameter]
    db = open_db()
    post = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (id,)
        ).fetchone()

    # check if the post exists i.e. in case the db returned a None value
    if post is None:
        abort(404, "Post id {0} doesn't exist").format(id)

    # if the post exists, then check if the author does NOT match the `id` of current user trying to delete the post
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    # this means it is now okay to delete the post
    return post


# Update Post Page view
@blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:  # the blog post needs to have a title, assign an error value
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = open_db()
            db.execute('UPDATE post SET title=?, body=? WHERE id = ?', (title, body, id))
            db.commit()  # save the changes
            return redirect(url_for('blog.index'))  # redirect back to index page after the update
    return render_template('blog/update.html', post=post)  # redirect back to update page if it is a `GET` request or there are issues with `initial update`


# Delete Post view [its template as been added to the update template]
@blueprint.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = open_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()  # save the data in the database
    return render_template('blog/index.html')  # redirect back to the index page
