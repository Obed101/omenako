from datetime import date, datetime
import os
from flask import render_template, request, url_for, flash, redirect, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from wtforms import StringField, SubmitField, PasswordField, RadioField, BooleanField, DateField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired as required, Length, EqualTo
from controller import app, db, ckeditor, change_in_db
from flask_ckeditor import CKEditorField
from models import UserModel, Notice, Assignment

admins = [4, 2]


class User(FlaskForm):
    """Creates a new user"""
    firstname = StringField('His First Name. Ex: John', [required()])
    lastname = StringField('His Last Name. Ex: Ayisi')
    question1 = PasswordField('Ask him to type "food" when prompted for favorite food')
    confirm = PasswordField('Repeat the answer', validators=[EqualTo(question1)])
    email = StringField('His Email Address (Optional)')
    omenako = BooleanField('Confirm he qualifies to have this account')
    role = RadioField('Is he an Elder or a Ministerial Servant?',
                      choices=[('MS', 'Ministerial Servant'),
                               ('Elder', 'Member Of The Body Of Elders')], validators=[required()])
    submit = SubmitField('Sign Up')


class UserProfile(FlaskForm):
    """modifies a user"""
    firstname = StringField('Your First Name')
    lastname = StringField('Your Last Name')
    question1 = PasswordField('Change Your Favorite food?')
    confirm = PasswordField('Repeat answer', validators=[EqualTo(question1)])
    email = StringField()
    submit = SubmitField()


class NoticeForm(FlaskForm):
    """Creates a form for Notice"""
    message = CKEditorField('Your notice body here', [
                            required('Please type your notice')])
    subject = StringField('Your notice title', [
                          required('Please type your notice title')])
    submit = SubmitField('Submit')


class AssignmentForm(FlaskForm):
    """Creates a form for Notice"""
    date = DateField(format="%d/%m/%Y")
    section = StringField('Treasures, Field Ministry, Living As Christians')
    typ = StringField('Example: Initial Call')
    name = StringField('Person Name')
    assistant = StringField('Name of assistant')
    tim = IntegerField('Enter the minutes')
    submit = SubmitField('Submit')


            # ############### #
            #                 #
            # Begin of Routes #
            #                 #
            # ############### #

@app.route('/')
def home():
    """Homepage"""
    return render_template('index.html', title='Home')


        ###### ASSIGNMENTS ACTIVITIES ######

@app.route('/assignments')
def assignments():
    """Displays The Assignments"""
    assign = Assignment.query.all()
    return render_template('assignments.html', title='Assignments', assignments=assign)


@app.route('/assignments/new', methods=['GET', 'POST'])
@login_required
def new_assignment():
    """Adds a new assignment"""
    if not current_user.role == 'Elder':
        flash('Only elders are allowed to add assignments')
        return redirect(url_for('assignments'))
    form = AssignmentForm()
    if form.is_submitted():
        assign = Assignment(section=form.section.data, typ=form.typ.data,
                            name=form.name.data, assist=form.assistant.data, tim=form.tim.data)
        assign.date = datetime.strptime(request.form['date'], '%Y-%m-%d').strftime("%d %B %Y")
        db.session.add(assign)
        db.session.commit()
        flash(f'Great! You added {form.name.data}\'s assignment')
        return redirect(url_for('assignments'))
    return render_template('new_assignment.html', title='Add Assignments', form=form)


@app.route('/assignments/<id>/delete')
@login_required
def delete_assignment(id):
    """Deletes an assignment"""
    if current_user.role == 'Elder':
        try:
            assign = Assignment.query.filter_by(id=id).first()
            assignee = assign.name
            assign.delete()
        except AttributeError:
            """To disable error if someone tries to delete a non existing node"""
            flash('It looks like that assignment does not exist')
            return redirect(url_for('assignments'))
        flash(f'You just deleted {assignee}\'s assignment')
    else:
        flash('Please ask Isaac Donkor or Moses Banfo to delete that')
    return redirect(url_for('assignments'))


        ##### NOTICE BOARD ACTIVITIES #####

@app.route('/notices')
@login_required
def notices():
    """Notice page handler"""
    user_form = User()
    return render_template('notices.html', title='Notices', form=user_form, Notice=Notice)


@app.route('/notices/new', methods=['GET', 'POST'])
@login_required
def new_notice():
    """Notice Creator"""
    form = NoticeForm()
    if form.is_submitted():
        notice = Notice(message=request.form.get('ckeditor'), subject=form.subject.data,
                        date=date.today().strftime('%A, %d %B %Y'), poster=f"{current_user.firstname} {current_user.lastname}")
        db.create_all()
        db.session.add(notice)
        db.session.commit()
        flash('Your Announcement has been posted successfully', 'success')
        return redirect(url_for('notices'))
    return render_template('new_notice.html', title='New Notice', ckeditor=ckeditor, form=form)


@app.route('/notices/<id>/delete')
def delete_notice(id):
    """Deletes a notice"""
    note = Notice.query.filter_by(id=id).first()
    if note:
        if f"{current_user.firstname} {current_user.lastname}" == note.poster or current_user.user_id in admins:
            note.delete()
            db.session.commit()
            flash('You have deleted that announcement')
        # For Account Requests
        elif not note.poster and current_user.role == 'Elder':
            note.delete()
            db.session.commit()
            flash('You have deleted that announcement')
        else:
            flash(f'Kindly ask {note.poster if note.poster else "an elder"} to delete this notice')
    else:
        flash('Sorry Post could not be deleted')
    return redirect(url_for('notices'))


        ##### PDF ROUTES #####

@app.route('/readers')
def readers():
    """Returns readers page in pdf"""
    pth = os.path.abspath(os.getcwd())
    fle = pth + '/templates/'
    return send_from_directory(fle, 'readers.pdf')


@app.route('/field_lead')
@login_required
def field_lead():
    """Returns field service leaders page in pdf"""
    pth = os.path.abspath(os.getcwd()) + '/templates/'
    return send_from_directory(pth, 'field_lead.pdf')


        ##### USERS AND ACCOUNTS #####

@app.route('/login', methods=['POST', 'GET'])
def login():
    """Login page"""
    user_form = User()
    if current_user.is_authenticated:
        flash('You are already signed in', 'warning')
        return redirect(url_for('assignments'))
    if user_form.is_submitted():
        user = UserModel.query.filter_by(firstname=user_form.firstname.data,
                                         question1=user_form.question1.data, lastname=user_form.lastname.data).first()
        if user:
            db.session.add(user)
            db.session.commit()
            login_user(user, True)
            if current_user.is_active:
                flash(f'You successfully logged in as {current_user.firstname} {current_user.lastname}', 'success')
            return redirect(request.args.get('next')) if request.args.get('next') else redirect(url_for('assignments'))
        else:
            flash('Invalid name or best food', 'error')
            return redirect(url_for('all_users'))
    return render_template('login.html', title='Login', form=user_form)


@app.route('/users')
@login_required
def all_users():
    """Returns all users"""
    users = UserModel.query.all()
    return render_template('users.html', users=users, title='All users', admins=admins)


@app.route('/users/<id>/delete')
@login_required
def delete_user(id):
    try:
        going = UserModel.query.filter_by(user_id=id).first()
        gone_name = going.firstname + ' ' + going.lastname
        his_id = going.user_id
        if going:
            if current_user.role == 'Elder' and his_id not in admins:
                going.delete()
                flash(f'You have deleted {gone_name if not current_user.user_id == his_id else "yourself"} successfully')
            elif his_id in admins and current_user.user_id in admins:
                going.delete()
                flash(f'You have deleted {gone_name if not current_user.user_id == his_id else "yourself"} successfully')
            elif his_id in admins and current_user.user_id not in admins:
                flash(f'You must be a secretary or a coordinator to delete {gone_name}')
            else:
                flash(f'Sorry, kindly ask an elder to remove {gone_name if not current_user.lastname in gone_name else "you"}')
        else:
            flash('Sorry, That was unsuccessful')
    except AttributeError:
        flash('Sorry, That was unsuccessful')
    return redirect(url_for('all_users'))


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    """ User Profile editor"""
    form = UserProfile()
    if form.is_submitted():
        current_user.firstname = change_in_db(current_user.firstname, form.firstname.data)
        current_user.lastname = change_in_db(current_user.lastname, form.lastname.data)
        current_user.email = change_in_db(current_user.email, form.email.data)
        current_user.question1 = change_in_db(current_user.question1, form.question1.data)
        db.session.commit()
        flash('Your profile has been updated successfully')
        return redirect(url_for('all_users'))
    return render_template('profile.html', form=form, title='Profile')


@app.route('/users/<id>/reset_question', methods=['GET'])
@login_required
def reset(id):
    """Reset a user's answer to best food question"""
    try:
        user = UserModel.query.filter_by(user_id=id).first()
        if current_user.user_id in admins:
            user.question1 = change_in_db(user.question1, 'food')
            db.session.commit()
            flash(f'You have reset {user.firstname}\'s best food successfully')
            return redirect(url_for('all_users'))
        else:
            flash(f'You are not allowed to reset {user.firstname}\'s question')
    except AttributeError:
        flash('Unable to delete a non-existing user')
        return redirect(url_for('all_users'))


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    """Create a new user"""
    user_form = User()
    if current_user.is_active:
        return redirect(url_for('add_user'))
    if user_form.is_submitted():
        if not user_form.omenako.data:
            flash('You must be in Omenako Congregation to use this site', 'error')
            return redirect(url_for('sign_up'))
        user = UserModel(firstname=user_form.firstname.data, lastname=user_form.lastname.data,
                         email=user_form.email.data, role=user_form.role.data, omenako=user_form.omenako.data, question1=user_form.question1.data)
        db.create_all()
        db.session.add(user)
        db.session.commit()
        login_user(user)
        if user.is_authenticated:
            flash('Congratulations, you just created an account', 'success')
            return redirect(url_for('assignments'))
        else:
            flash('unable to login')
    return render_template('signup.html', title='Create Account', form=user_form)


@app.route('/users/new', methods=['POST', 'GET'])
@login_required
def add_user():
    """Create a new user"""
    if current_user.role == 'Elder':
        user_form = User()
        if user_form.is_submitted():
            if not user_form.omenako.data:
                flash('The new user must be a member of Omenako Congregation')
                return redirect(url_for('assignments'))
            user = UserModel(firstname=user_form.firstname.data, lastname=user_form.lastname.data,
                             email=user_form.email.data, role=user_form.role.data, omenako=user_form.omenako.data, question1='food')
            db.create_all()
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('all_users'))
    else:
        flash('Only Elders can add new users')
        return redirect(url_for('all_users'))
    return render_template('add_user.html', title='Create Account', form=user_form)


@app.route('/request_account', methods=['GET', 'POST'])
def request_account():
    """Allows unauthorised users to request an account to be created"""
    form = User()
    if current_user.is_active:
        flash('You are already authenticated')
        return redirect(url_for('home'))
    if form.is_submitted():
        req = Notice(subject='New account request detected!',
                     message=f'''Name: <b>{form.firstname.data}</b>
                     <br> On <b>{date.today().strftime('%A, %d %B %Y')}</b>
                     <br> Please add him if you think he qualifies''')
        db.session.add(req)
        db.session.commit()
        if req:
            flash('Congrats! Your request has been submitted successfully')
            return redirect(url_for('home'))
        else:
            flash('Sorry, that wasn\'t successful please try again')
    return render_template('request_account.html', form=form, title='Request Account')


@app.route('/logout')
def logout():
    """Logout page"""
    logout_user()
    flash('You are logged out now!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
