import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import sqlite3
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the path to the SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'election_data.db')

def get_election_data(year=None, office_code=None):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT
        e.year,
        p.municipality_name,
        p.precinct_code,
        off.office_code,
        off.name AS office_name,
        pa.party_code,
        r.vote_total
    FROM
        results r
    JOIN
        elections e ON r.election_id = e.id
    JOIN
        precincts p ON r.precinct_id = p.id
    JOIN
        parties pa ON r.party_id = pa.id
    JOIN
        offices off ON r.office_id = off.id
    WHERE
        pa.party_code IN ('DEM', 'REP')
    """
    params = []
    if year:
        query += " AND e.year = ?"
        params.append(year)
    if office_code:
        query += " AND off.office_code = ?"
        params.append(office_code)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_registration_data(year=None):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT
        e.year,
        p.municipality_name,
        p.precinct_code,
        pa.party_code,
        reg.registered_voters
    FROM
        registration reg
    JOIN
        elections e ON reg.election_id = e.id
    JOIN
        precincts p ON reg.precinct_id = p.id
    JOIN
        parties pa ON reg.party_id = pa.id
    WHERE
        pa.party_code IN ('DEM', 'REP')
    """
    params = []
    if year:
        query += " AND e.year = ?"
        params.append(year)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Get available years and offices for dropdowns
conn = sqlite3.connect(DB_PATH)
available_years = pd.read_sql_query("SELECT DISTINCT year FROM elections ORDER BY year DESC", conn)['year'].tolist()
available_offices = pd.read_sql_query("SELECT DISTINCT office_code, name FROM offices WHERE office_code IN ('USP', 'GOV', 'USSN', 'ATTYG', 'AUDG', 'TREAS', 'REPR', 'STSEN', 'STH') ORDER BY office_code", conn)
conn.close()

office_options = [{'label': f"{row['name']} ({row['office_code']})", 'value': row['office_code']} for index, row in available_offices.iterrows()]

# Define the app layout
app.layout = html.Div(children=[
    html.H1(children='Election Statistics Dashboard'),

    html.Div(children='''
        Diverging Bar Chart: DEM vs REP votes and voter registrations per precinct.
    '''),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in available_years],
            value=available_years[0] if available_years else None, # Default to most recent year
            clearable=False
        )
    ]),

    html.Div([
        html.Label("Select Office:"),
        dcc.Dropdown(
            id='office-dropdown',
            options=office_options,
            value='USP', # Default value
            clearable=False
        )
    ]),

    html.Div([
        html.Label("Sort By:"),
        dcc.Dropdown(
            id='sort-dropdown',
            options=[
                {'label': 'Votes', 'value': 'votes'},
                {'label': 'Precinct ID', 'value': 'precinct_id'}
            ],
            value='votes', # Default sort by votes
            clearable=False
        )
    ]),

    dcc.Graph(
        id='diverging-bar-chart',
        figure={} # Will be updated by callback
    )
])

# Callback to update the diverging bar chart based on dropdown selections
@app.callback(
    Output('diverging-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('office-dropdown', 'value'),
    Input('sort-dropdown', 'value')
)
def update_chart(selected_year, selected_office, sort_by):
    if not selected_year or not selected_office or not sort_by:
        return {}

    # Get election data for the selected year and office
    df_election_filtered = get_election_data(year=selected_year, office_code=selected_office)
    
    # Aggregate votes by precinct and party
    df_votes_pivot = df_election_filtered.groupby(['municipality_name', 'precinct_code', 'party_code'])['vote_total'].sum().unstack(fill_value=0).reset_index()
    df_votes_pivot['vote_difference'] = df_votes_pivot['DEM'] - df_votes_pivot['REP']

    # Get registration data for the selected year
    df_registration_filtered = get_registration_data(year=selected_year)
    
    # Aggregate registered voters by precinct and party
    df_reg_pivot = df_registration_filtered.groupby(['municipality_name', 'precinct_code', 'party_code'])['registered_voters'].sum().unstack(fill_value=0).reset_index()
    df_reg_pivot['registration_difference'] = df_reg_pivot['DEM'] - df_reg_pivot['REP']

    # Merge election and registration data
    df_merged = pd.merge(df_votes_pivot, df_reg_pivot, on=['municipality_name', 'precinct_code'], how='left', suffixes=('_votes', '_reg'))
    df_merged['registration_difference'] = df_merged['registration_difference'].fillna(0) # Fill NaN for precincts without registration data

    # Prepare data for stacked diverging bar chart
    df_merged['DEM_votes_pos'] = df_merged['DEM_votes']
    df_merged['REP_votes_neg'] = -df_merged['REP_votes']
    df_merged['DEM_reg_pos'] = df_merged['DEM_reg']
    df_merged['REP_reg_neg'] = -df_merged['REP_reg']

    df_plot = df_merged[[
        'municipality_name', 'precinct_code',
        'DEM_votes_pos', 'REP_votes_neg',
        'DEM_reg_pos', 'REP_reg_neg'
    ]].copy()

    df_plot['precinct_display'] = df_plot['municipality_name'] + ' - ' + df_plot['precinct_code']

    df_plot_melted = df_plot.melt(
        id_vars=['precinct_display', 'municipality_name', 'precinct_code'],
        value_vars=['DEM_votes_pos', 'REP_votes_neg', 'DEM_reg_pos', 'REP_reg_neg'],
        var_name='party_type',
        value_name='value'
    )

    df_plot_melted = df_plot_melted[df_plot_melted['value'] != 0]

    if df_plot_melted.empty:
        return {} # Return empty figure if no data to display

    if sort_by == 'votes':
        # Sort by absolute value of the combined difference for top N, then by value for diverging display
        # First, calculate a combined absolute difference for sorting precincts
        df_plot_melted['abs_combined_diff'] = df_plot_melted.groupby('precinct_display')['value'].transform(lambda x: x.abs().sum())
        
        # Get top 150 precincts based on this combined absolute difference
        top_precincts_for_sorting = df_plot_melted.drop_duplicates(subset=['precinct_display']).sort_values(by='abs_combined_diff', ascending=False).head(150)
        ordered_precincts = top_precincts_for_sorting.sort_values(by='value', ascending=True)['precinct_display'].tolist()

        # Filter melted dataframe to only include top precincts and sort for display
        df_plot_melted = df_plot_melted[df_plot_melted['precinct_display'].isin(ordered_precincts)]
        df_plot_melted['precinct_display'] = pd.Categorical(df_plot_melted['precinct_display'], categories=ordered_precincts, ordered=True)
        df_plot_melted = df_plot_melted.sort_values(by=['precinct_display', 'value'], ascending=[True, False])
    elif sort_by == 'precinct_id':
        # Sort by precinct_code directly
        ordered_precincts = sorted(df_plot_melted['precinct_display'].unique())
        df_plot_melted['precinct_display'] = pd.Categorical(df_plot_melted['precinct_display'], categories=ordered_precincts, ordered=True)
        df_plot_melted = df_plot_melted.sort_values(by=['precinct_display', 'value'], ascending=[True, False])

    colors = {
        'DEM_votes_pos': 'blue',
        'REP_votes_neg': 'red',
        'DEM_reg_pos': 'lightblue',
        'REP_reg_neg': 'lightcoral'
    }

    fig = px.bar(
        df_plot_melted,
        x='value',
        y='precinct_display',
        color='party_type',
        color_discrete_map=colors,
        orientation='h',
        barmode='relative',
        title=f'DEM vs REP Votes and Registrations by Precinct for {selected_office} ({selected_year})',
        labels={'value': 'Count', 'precinct_display': 'Precinct'},
        hover_data={
            'value': ':.0f',
            'party_type': True,
            'municipality_name': False,
            'precinct_code': False
        }
    )
    fig.update_layout(
        yaxis={'categoryorder':'array', 'categoryarray': ordered_precincts},
        height=max(600, len(ordered_precincts) *10)
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)