from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, VBar, ColumnDataSource


def bar_plot(x, y, title='', x_title='', y_title='', x_labels=None):
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