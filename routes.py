from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required,\
    logout_user
from models import Admin_User, Quests, Answs, Results
from UserLogin import UserLogin
from werkzeug.security import check_password_hash
from app_config import app, db, login_manager, SESSION_TIME
from admin import admin


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(Admin_User, user_id)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        text = Quests.query.all()
        answers = Answs.query.all()

        return render_template('index.html', text=text, answers=answers)

    input_login = request.form['login']
    input_password = request.form['password']
    admin_query = Admin_User.query.all()
    for row in admin_query:
        if input_login == row.login and check_password_hash(row.password, input_password):
            user = UserLogin().create(row)
            login_user(user, duration=SESSION_TIME)
            return redirect(url_for('admin.index'))

    flash('Неверный логин или пароль')
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_panel():
    return render_template(url_for('admin.index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/successful')
def succ():
    return render_template('successful.html')


@app.route('/unsuccessful')
def unsucc():
    return render_template('unsuccessful.html')


@app.route('/survey_form', methods=['POST', 'GET'])
def form():
    results = []
    num = Quests.query.all()

    for quest in num:
        results.append(request.form[f'group{quest.quest_id}'])

    name = request.form['fio']
    res = " ".join(results)
    user_res = Results(name=name, result=res)
    try:
        db.session.add(user_res)
        db.session.commit()
    except Exception as error:
        print(error)
        return redirect(url_for('unsucc'))

    return redirect(url_for('succ'))
