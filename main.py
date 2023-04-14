import sqlite3
import pandas as pd
import plotly.express as exp
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import ceil

from queries import (team_build_type_query, team_build_type_by_users_and_bots_query,
                     team_build_type_by_maps_query, ship_effectivity_query)

con = sqlite3.connect("Dataset.db")

# Запрос о количестве участников, выбравших тот или иной тип боя"
query = team_build_type_query

# Получаем датафрейм и строим круговую диаграмму
df = pd.read_sql(query, con)

fig = exp.pie(df, values="amount_members", names="team_build_type",
              title="Популярность типов боя среди игроков",
              width=800, height=800)
fig.update_layout(title_x=0.5, title_font=dict(size=26))
fig.update_traces(textinfo='value+percent', textfont_size=14)
fig.show()

# Запрос о количестве участников, выбравших тот или иной тип боя сгруппированный среди реальных пользователей и ботов"
query_1 = team_build_type_by_users_and_bots_query

# Получаем датафрейм и строим две совмещенные круговые диаграммы
df_1 = pd.read_sql(query_1, con)

fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
fig.add_trace(go.Pie(labels=df_1["team_build_type"], values=df_1[df_1["users"] == 1]["amount_members"], name="Users"),
              1, 1)
fig.add_trace(go.Pie(labels=df_1["team_build_type"], values=df_1[df_1["users"] == 0]["amount_members"], name="Bots"),
              1, 2)

fig.update_traces(hole=.3, hoverinfo="label+percent+name", textinfo='value+percent', textfont_size=14)

fig.update_layout(
    title_text="Популярность типов боя среди пользователей и ботов",
    width=1200, height=800,
    title_x=0.5, title_font=dict(size=26),
    annotations=[dict(text='Users', x=0.19, y=0.5, font_size=22, showarrow=False),
                 dict(text='Bots', x=0.8, y=0.5, font_size=22, showarrow=False)])
fig.show()

# Запрос о количестве разных типов боев, сгруппированных по типам карт
query_2 = team_build_type_by_maps_query

# Получаем датафрейм и строим точечную диаграмму распределения количетсва разных типов боев для разных карт
df_2 = pd.read_sql(query_2, con)

fig = exp.scatter(data_frame=df_2, x="map_type", y="amount", color="team_build_type",
                  title="Распределение колчества разных типов боев в зависимости от типа карты",
                  width=1200, height=700)

fig.update_traces(marker_size=10)
fig.update_layout(title_x=0.5, title_font=dict(size=26))
fig.update_yaxes(dtick=500, title_font={'size': 16}, title_text='Amount of arenas')
fig.update_xaxes(title_font={'size': 16}, title_text='Maps type')

fig.show()

# Запрос для анализа эффективности кораблей
query_3 = ship_effectivity_query

# Получим датафрейм и добавим к нему колонку, объединяющую название корабля и страну
df_3 = pd.read_sql(query_3, con)
df_3["name"] = df_3['ship_name'] + ', ' + df_3['country']

# Строим горизонтальные столбчатые диаграммы c цветовой палитрой, от зеленого - лучшие показатели, до красного - худшие
ship_classes = list(df_3["ship_class"].unique())
heigths = []
for ship_class in ship_classes:
    data = df_3[df_3["ship_class"] == ship_class]
    heigths.append(len(data) / len(df_3))

params = ["alived", "winner", "frags", "positive_damage", "avg(exp)", "avg(distance)"]
mins = list(map(min, [df_3[param] for param in params]))
maxs = list(map(max, [df_3[param] for param in params]))

column_titles = ["Процент выживаемости", "Процент побед", "Среднее кол-во фрагов",
                 "Сред. положит. урон", "Средний опыт", "Средняя дистанция"] * len(ship_classes)

fig = make_subplots(rows=len(ship_classes), cols=len(params), subplot_titles=column_titles,
                    row_titles=(list(ship_classes)),
                    shared_yaxes=True, vertical_spacing=0.01, horizontal_spacing=0,
                    row_heights=heigths)

for i, ship_class in enumerate(ship_classes, start=1):
    data = df_3[df_3["ship_class"] == ship_class]
    z = len(data)
    for j, param in enumerate(params, start=1):
        fig.add_trace(go.Bar(x=data[param], y=data["name"], text=data[param], marker_color=data[param],
                             marker_cmin=mins[j - 1], marker_cmax=maxs[j - 1]), i, j)
        fig.update_xaxes(range=[0, ceil(maxs[j - 1])], row=i, col=j)

    fig.update_yaxes(nticks=z, secondary_y=True)

fig.update_traces(orientation='h', texttemplate='%{x:.2f}', textfont_size=10, textposition='outside',
                  marker_colorscale=[[0, 'rgb(250,5,34)'], [0.5, 'rgb(250,136,5)'], [1.0, 'rgb(5,250,29)']])
fig.update_layout(showlegend=False, width=1200, height=4000, title="Оценка эффективности кораблей",
                  title_font={'size': 24}, title_x=0.5)
fig.update_xaxes(showticklabels=False, showgrid=False)
fig.update_annotations(font_size=12)
for i in fig['layout']['annotations'][:-5:-1]:
    i['font'] = dict(size=20)

fig.show()
