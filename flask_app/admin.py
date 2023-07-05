from flask import abort
from flask_admin import expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user
from collections import namedtuple
from models import Quests, Results, Answs
from app_config import app, db
from plots import bar_plot


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
            summary = 0
            for el2 in users_res:
                summary += el2[i]
            answ_sum.append(summary)

        avrg_answ_sum = []
        for i in range(len(quests_id)):
            summ = 0
            for el2 in users_res:
                summ += el2[i]
            summ /= len(users_res)
            avrg_answ_sum.append(summ)

        plots = namedtuple('Plots', 'script, div')

        plot1 = plots(*bar_plot(
            res_ids[:],
            final_res[:],
            "Диаграмма баллов у сотрудников",
            "Сотрудники",
            "Баллы",
            users
        ))
        plot2 = plots(*bar_plot(
            quests_id[:],
            answ_sum[:],
            "Диаграмма набранных баллов по каждому вопросу",
            "Вопросы",
            "Баллы"
        ))
        plot3 = plots(*bar_plot(
            quests_id[:],
            avrg_answ_sum[:],
            "Диаграмма набранных в среднем баллов по каждому вопросу",
            "Вопросы",
            "Средний балл"
        ))

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
