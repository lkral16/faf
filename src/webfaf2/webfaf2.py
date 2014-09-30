import os

import flask
from flask import Flask, redirect
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy

from pyfaf.storage.user import User

app = Flask(__name__)

if "WEBFAF_ENVIRON_PRODUCTION" in os.environ:
    app.config.from_object('config.ProductionConfig')
elif "WEBFAF_ENVIRON_TEST" in os.environ:
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)
oid = OpenID(app, safe_roots=[])

from login import login
app.register_blueprint(login)
from dumpdirs import dumpdirs
app.register_blueprint(dumpdirs, url_prefix="/dumpdirs")
from reports import reports
app.register_blueprint(reports, url_prefix="/reports")
from problems import problems
app.register_blueprint(problems, url_prefix="/problems")
from stats import stats
app.register_blueprint(stats, url_prefix="/stats")
from summary import summary
app.register_blueprint(summary, url_prefix="/summary")

from filters import problem_label, fancydate, timestamp
app.jinja_env.filters['problem_label'] = problem_label
app.jinja_env.filters['fancydate'] = fancydate
app.jinja_env.filters['timestamp'] = timestamp

from utils import fed_raw_name, WebfafJSONEncoder
app.json_encoder = WebfafJSONEncoder


@app.route('/')
def hello_world():
    return redirect(flask.url_for("summary.index"), code=302)


@app.before_request
def before_request():
    flask.g.user = None
    if "openid" in flask.session:
        username = fed_raw_name(flask.session["openid"])
        flask.g.user = (db.session.query(User)
                        .filter(User.username == username)
                        .first())


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413

if __name__ == '__main__':
    app.run()