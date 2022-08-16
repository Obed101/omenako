from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_ckeditor import CKEditor
from flask_login import current_user

app = Flask(__name__)

app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'no one can guess this key im using for this project'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)

db = SQLAlchemy(app)


def change_in_db(old, new):
    """Modifies old data in database"""
    if old == current_user.question1:
        """Handle answer for best food differently"""
        old = new if new and not new == old else old
    else:
        old = new if not new == old else old
    db.session.commit()
    return old
