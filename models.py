"""Handling database requests"""

from flask_login import LoginManager, UserMixin
from sqlalchemy import delete
# from werkzeug.security import generate_password_hash, check_password_hash
from controller import app, db
login = LoginManager(app)
login.login_view = 'login'


@login.user_loader
def load_user(id):
    return UserModel.query.get(id)


class UserModel(UserMixin, db.Model):
    """A user instance"""
    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(100))
    role = db.Column(db.String(30))
    omenako = db.Column(db.Boolean())
    question1 = db.Column(db.String(40))
    
    def get_id(self):
        return self.user_id
    
    def delete(self):
        """Deletes a notice"""
        db.session.delete(self)
        db.session.commit()

class Notice(db.Model):
    """Notice message saver"""
    id = db.Column(db.Integer(), db.Identity(start=1, cycle=True), primary_key=True)
    subject = db.Column(db.String(80))
    message = db.Column(db.String(300))
    poster = db.Column(db.String(50))
    date = db.Column(db.String())

    def delete(self):
        """Deletes a notice"""
        db.session.delete(self)
        db.session.commit()



class Assignment(db.Model):
    """Assignment Creator"""
    id = db.Column(db.Integer(), db.Identity(start=1, cycle=True), primary_key=True)
    date = db.Column(db.String())
    section = db.Column(db.String(50))
    typ = db.Column(db.String(50))
    name = db.Column(db.String(50))
    assist = db.Column(db.String(50))
    tim = db.Column(db.Integer())

    def delete(self):
        """Deletes an assignment"""
        db.session.delete(self)
        db.session.commit()

db.create_all()
db.session.commit()
