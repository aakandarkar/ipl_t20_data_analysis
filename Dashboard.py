import dash
import plotly.express as px
import pandas as pd
import os
import plotly.graph_objs as go
from dash import dcc, html
from base64 import b64encode
import io

current_dir = os.getcwd()
buffer = io.StringIO()

df_list = []
for year in range(2008, 2024):
    filename = f"{current_dir}/csv_data/batting_df_{year}.csv"
    df = pd.read_csv(filename)
    df['season_year'] = year
    df_list.append(df)
batting_df = pd.concat(df_list)

team_wins_df = pd.read_csv(current_dir+"/csv_data/team_wins.csv")

drop_down_options = []
flag = True
for year in range(2008, 2024):
    if flag:
        data = {
            'label': "All Years",
            'value': "All"
        }
        drop_down_options.append(data)
        flag=False
    json_data = {
        'label': year,
        'value': year
    }
    drop_down_options.append(json_data)


season_group = batting_df.groupby(['season_year', 'Player'], as_index=False)
season_player_runs = season_group['Runs'].sum()
season_player_runs.sort_values(['season_year', 'Runs'], ascending=[True, False], inplace=True)
top10_batsmen_season = pd.DataFrame()
for season in range(2008, 2024):
    season_data = season_player_runs[season_player_runs['season_year'] == season].head(10)
    top10_batsmen_season = pd.concat([top10_batsmen_season, season_data])

pivot_data = top10_batsmen_season.pivot(index='Player', columns='season_year', values='Runs').fillna(0)
years = [{'label': str(year), 'value': str(year)} for year in sorted(top10_batsmen_season['season_year'].unique())]
players = [{'label': player, 'value': player} for player in sorted(top10_batsmen_season['Player'].unique())]


merged_df = pd.merge(batting_df, team_wins_df, left_on="team", right_on="winning_team")
top_batsmen_df = merged_df.loc[merged_df.groupby(["winning_team", "winning_year"])["Runs"].idxmax()]

html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='IPL Data Analysis'),

    # Add a dropdown to select the year
    dcc.Dropdown(
        id='year-dropdown',
        options=drop_down_options,
        value='All',  # Default value is 'All' years
    ),
    dcc.Graph(id='box-plot',),
    dcc.Graph(id='pie-chart',),

    html.H1('Runs Scored by Top 10 IPL Batsman in Each Season (2008-2023)'),
    html.Div([
        html.Label('Select Year'),
        dcc.Dropdown(
            id='heat-year-dropdown',
            options=[{'label': 'All Years', 'value': 'All'}] + years,
            value='All'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        html.Label('Select Player'),
        dcc.Dropdown(
            id='player-dropdown',
            options=[{'label': 'All Players', 'value': 'All'}] + players,
            value='All'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    dcc.Graph(id='heatmap-graph'),

    html.H2("Team Wins and Top Batsman Comparison"),
    html.Div([
        dcc.Dropdown(
            id="team-dropdown",
            options=[{"label": team, "value": team} for team in merged_df["team"].unique()],
            value="MI"
        ),
        dcc.Graph(
            id="team-wins-vs-top-batsman-graph"
        ),
    ]),

])

@app.callback(
    [dash.dependencies.Output('box-plot', 'figure'),
     dash.dependencies.Output('pie-chart', 'figure'),
     dash.dependencies.Output('heatmap-graph', 'figure'),
     dash.dependencies.Output("team-wins-vs-top-batsman-graph", "figure")],
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('heat-year-dropdown', 'value'),
     dash.dependencies.Input('player-dropdown', 'value'),
     dash.dependencies.Input("team-dropdown", "value")])
def update_plots(year,selected_year, selected_player,team):
    if year == 'All':
        data = batting_df
    else:
        data = batting_df[batting_df['season_year'] == int(year)]
    team_runs = data.groupby(['team'])['Runs'].sum().reset_index()
    sorted_runs = pd.DataFrame(team_runs).sort_values(by='Runs',ascending=False)
    fig_runs_teams = px.bar(sorted_runs, x='team', y='Runs', color='team', title='Total Runs Scored by Each Team (2008-2023)')
    fig_runs_teams.update_xaxes(title='Teams')
    fig_runs_teams.write_html(buffer)

    top_batsmen = data.groupby('Player')['Runs'].sum().reset_index().sort_values('Runs', ascending=False).head(10)
    fig_top_batsman = px.pie(top_batsmen, values='Runs', names='Player', title=f'Top 10 Batsmen ({year})',
                     color_discrete_sequence=px.colors.sequential.RdBu)
    fig_top_batsman.update_traces(textposition='inside', textinfo='label+value')
    fig_top_batsman.update_layout(showlegend=False,width=800, height=600,margin=dict(t=50, b=50, l=50, r=50))
    fig_top_batsman.write_html(buffer)
    filtered_data = top10_batsmen_season
    if selected_year != 'All':
        filtered_data = filtered_data[filtered_data['season_year'] == int(selected_year)]
    if selected_player != 'All':
        filtered_data = filtered_data[filtered_data['Player'] == selected_player]

    pivot_data = filtered_data.pivot(index='Player', columns='season_year', values='Runs').fillna(0)
    heatmap_trace = go.Heatmap(
        x=pivot_data.columns,
        y=pivot_data.index,
        z=pivot_data.values,
        colorscale='YlGnBu',
        zmin=0,
        zmax=pivot_data.max().max(),
        hovertemplate='Player: %{y}<br>Year: %{x}<br>Runs Scored: %{z}<extra></extra>'
    )
    heatmap_layout = go.Layout(
        xaxis={'title': 'Season Year'},
        yaxis={'title': 'Player'},
        margin={'l': 100, 'r': 10, 't': 50, 'b': 100},
        height=800
    )
    heatmap_fig = {'data': [heatmap_trace], 'layout': heatmap_layout}
    team_df = merged_df.loc[merged_df["team"] == team]
    team_wins_vs_top_batsman_graph = px.scatter(
        team_df, x="winning_year", y="Runs", color="Player",
        title=f"{team} Wins vs Top Batsman Comparison", labels={"winning_year": "Year"}
    )
    team_wins_vs_top_batsman_graph.write_html(buffer)

    return fig_runs_teams, fig_top_batsman, heatmap_fig,team_wins_vs_top_batsman_graph



if __name__ == '__main__':
    app.run_server(debug=True)

