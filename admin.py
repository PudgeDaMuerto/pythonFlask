from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, VBar, ColumnDataSource
from flask import abort

from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

from flask_login import current_user

from collections import namedtuple

from models import Quests, Results


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
