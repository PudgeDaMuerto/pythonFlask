from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, VBar, ColumnDataSource

import flask
from flask import Flask, render_template, request, redirect, url_for, abort

from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin.menu import MenuLink

from flask_login import LoginManager, login_user, login_required,\
    logout_user, current_user

from models import *
from UserLogin import UserLogin

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from collections import namedtuple

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'an(v$g+fv=&5%bp*-nt)rkv6y1^vi)v%ew_sm_p8sqiseyjrh%'
app.config['SQLALCHEMY_ECHO'] = False
db.init_app(app)
login_manager = LoginManager(app)


class AdminView(ModelView):
    column_display_pk = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(401)


class HomeAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        res = Results.query.all()
        quests = Quests.query.all()

        users = [user.name for user in res]
        res_ids = [user.res_id for user in res]
        users_res = [user.result for user in res]

        final_res = []
        for i in range(len(users_res)):
            users_res[i] = users_res[i].split()
            users_res[i] = list(map(int, users_res[i]))
            final_res.append(sum(users_res[i]))

        quests_id = [quest.quest_id for quest in quests]
        quests_names = [quest.quest_text for quest in quests]
        quests_dict = dict(zip(quests_id, quests_names))

        answ_sum = []
        for i in range(len(quests_id)):
            summ = 0
            for el2 in users_res:
                summ += el2[i]
            answ_sum.append(summ)

        avrg_answ_sum = []
        for i in range(len(quests_id)):
            summ = 0
            for el2 in users_res:
                summ += el2[i]
            summ /= len(users_res)
            avrg_answ_sum.append(summ)

        def create_bar(x, y, title='', x_title='', y_title='', x_labels=None):
            bar_data = {'x': x, 'y': y}
            source = ColumnDataSource(bar_data)
            plot = figure(title=title, x_axis_label=x_title, y_axis_label=y_title, width=500, height=500)
            glyph = VBar(x='x', top='y', width=.8, bottom=0, fill_color='#66FFFF')
            hover_html = """
                          <div>
                            <span class="hover-tooltip">ID @x</span>
                          </div>
                          <div>
                            <span class="hover-tooltip">{} @y</span>
                          </div>
                        """.format(y_title)
            tools = HoverTool(tooltips=hover_html)
            plot.add_tools(tools)
            plot.add_glyph(source, glyph)
            if x_labels:
                plot.xaxis.ticker = x
                plot.xaxis.major_label_overrides = dict((zip(x, x_labels)))
            plot.toolbar.autohide = True

            script, div = components(plot)

            return script, div

        plots = namedtuple('Plots', 'script, div')

        plot1 = plots(*create_bar(res_ids[:], final_res[:], 'Диаграмма баллов у сотрудников', "Сотрудники", "Баллы", users))
        plot2 = plots(*create_bar(quests_id[:], answ_sum[:],
                                  "Диаграмма набранных баллов по каждому вопросу", "Вопросы", "Баллы"))
        plot3 = plots(*create_bar(quests_id[:], avrg_answ_sum[:],
                                  "Диаграмма набранных в среднем баллов по каждому вопросу", "Вопросы", "Средний балл"))

        context = {
            'plot1': plot1,
            'plot2': plot2,
            'plot3': plot3,
            'quests_dict': quests_dict
        }

        return self.render('admin_home.html', context=context)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(401)


class AdminAnswersView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('answer_id', 'text', 'value', 'quest_id')
    form_columns = ('text', 'value', 'quest_id')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(401)


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
    print(generate_password_hash("admin"))
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
