import flask
from flask import Flask, render_template, request, redirect, url_for, abort

from flask_admin import Admin
from flask_admin.menu import MenuLink

from flask_login import LoginManager, login_user, login_required,\
    logout_user

from models import *
from UserLogin import UserLogin

from werkzeug.security import check_password_hash
from datetime import timedelta

from admin import HomeAdminView, AdminView, AdminAnswersView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'an(v$g+fv=&5%bp*-nt)rkv6y1^vi)v%ew_sm_p8sqiseyjrh%'
app.config['SQLALCHEMY_ECHO'] = False
db.init_app(app)
login_manager = LoginManager(app)

admin = Admin(app, 'Админ панель', index_view=HomeAdminView(name='Home'), template_mode='bootstrap3')
admin.add_view(AdminView(Quests, db.session, name='Вопросы'))
admin.add_view(AdminAnswersView(Answs, db.session, name='Ответы'))
admin.add_view(AdminView(Results, db.session, name='Результаты'))
admin.add_link(MenuLink(name='Вернуться на главную', category='', url='/'))


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(Admin_User, user_id)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        input_login = request.form['login']
        input_password = request.form['password']
        admin = Admin_User.query.all()
        print(admin)

        for i in range(len(admin)):
            if input_login == admin[i].login and check_password_hash(admin[i].password, input_password):
                user = UserLogin().create(admin[i])
                login_user(user, duration=timedelta(minutes=30))
                return redirect(url_for('admin.index'))

        flask.flash('Неверный логин или пароль')
        return redirect(url_for('index'))

    else:
        text = Quests.query.all()
        answers = Answs.query.all()
        return render_template('index.html', text=text, answers=answers)


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
    except Exception:
        return redirect(url_for('unsucc'))

    return redirect(url_for('succ'))


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
    # serve(app, host='localhost', port=5000)
