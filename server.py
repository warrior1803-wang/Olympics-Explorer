import altair as alt
alt.data_transformers.enable('default', max_rows=None)
import pandas as pd
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)
import json
import random


@app.route("/")
def index():
    return render_template("index.html", title="Visualization Demo")


@app.route("/team_data")
def team_data():
    df = df_olympics
    team = request.args.getlist("team[]")
    year_max = int(request.args.get("year_max", df.year.max()))  # if 'year_max' not found, use df.year.max()
    year_min = int(request.args.get("year_min", df.year.min()))
    team_filter = " or ".join(["team =='{}'".format(t) for t in team])
    
    query_str = "medal==medal"  # filter out NaN values in the 'medal' column
    query_str += " and ({}) and season=='Summer'".format(team_filter)
    query_str += " and (year >= {} and year <= {})".format(year_min, year_max)
    print(query_str)
    df = df.query(query_str)
    df = df.groupby(["team", "year"]).size().reset_index(name='count')
    fig1 = alt.Chart(df, width=800).mark_line().encode(
        alt.X("year:N", title="年份"),
        alt.Y("count", title="奖牌数量"),
        color="team:N",
    )
    fig2 = alt.Chart(df).mark_bar().encode(
        alt.X("team:N", title="代表队"),
        alt.Y("sum(count):Q", title="历年奖牌总数"),
        color="team:N"
    )
    fig = fig1 | fig2
    fig_json = json.loads(fig.to_json())
    return jsonify({
        "figure": fig_json,
        "teams": [t for t in df_olympics.team.unique()],
        "years": {"max": year_max, "min": year_min},
    })


if __name__ == '__main__':
    df_olympics = pd.read_csv("athlete_events.csv")
    app.run(debug=True)
