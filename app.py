import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from coincap import *
from sendemail import send_mail

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY], )

app.title = 'Coincap'

LOGO_URL = 'https://avatars.githubusercontent.com/u/5997976?s=200&v=4'

navbar = dbc.Navbar(id='navbar', children=[

    html.A(
        dbc.Row([
            dbc.Col(html.Img(src=LOGO_URL, height="70px")),
            dbc.Col(
                dbc.NavbarBrand("Coin Live Tracker",
                                style={'color': 'black', 'fontSize': '25px', 'fontFamily': 'Times New Roman'}
                                )

            )

        ], align="center",
            no_gutters=True),
        href='https://github.com/zaqxsw800402/coincap_dash'
    ),
    dbc.Button(id='button', children="Say Hi!", color="primary", className='ml-auto',
               href='https://github.com/zaqxsw800402/coincap_dash')

])

coins = select_all()


def data_for_cases(rank):
    rank_df = select_rankid(rank)
    rank_id = rank_df['id'][0]
    rank_price = rank_df['priceUsd'][0]
    return [
        dbc.CardHeader(f'Rank {rank}'),
        dbc.CardBody(
            [
                dcc.Markdown(
                    dangerously_allow_html=True,
                    children=[
                        "{0} <br><sub>{1}</sub></br>".format(
                            rank_id, rank_price
                        )
                    ],
                )
            ]
        ),
    ]


body_app = dbc.Container([

    dbc.Row(html.Marquee("Coincap with dash and plotly"),
            style={'color': 'green'}),

    dbc.Row([
        dbc.Col(dbc.Card(data_for_cases(1), color='primary',
                         style={'text-align': 'center'}, inverse=True), xs=12, sm=12, md=4, lg=4, xl=4,
                style={'padding': '12px 12px 12px 12px'}),

        dbc.Col(dbc.Card(data_for_cases(2), color='success',
                         style={'text-align': 'center'}, inverse=True), xs=12, sm=12, md=4, lg=4, xl=4,
                style={'padding': '12px 12px 12px 12px'}),

        dbc.Col(dbc.Card(data_for_cases(3), color='danger',
                         style={'text-align': 'center'}, inverse=True), xs=12, sm=12, md=4, lg=4, xl=4,
                style={'padding': '12px 12px 12px 12px'}),

    ]),

    html.Br(),
    html.Br(),

    dbc.Row([html.Div(html.H4('Choose one coin '),
                      style={'textAlign': 'center', 'fontWeight': 'bold', 'family': 'georgia', 'width': '100%'})]),

    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col(
            [html.Div(id='dropdown-div',
                      children=[dcc.Dropdown(id='coin-dropdown',
                                             options=[{'label': i, 'value': i} for i in
                                                      np.append(['All'], coins['id'].unique())],
                                             value='All',
                                             placeholder='Select the coin'
                                             )], style={'width': '100%', 'display': 'inline-block'}),

             html.Div(id='coin-table-output')
             ], style={'height': '450px', 'text-align': 'center'}, xs=12, sm=12, md=6, lg=6, xl=6),

        dbc.Col([dbc.Card(id='coin-graph', style={'height': '450px'})], )

    ]),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col(
            html.Div(dcc.Dropdown(id='coin-buy',
                                  options=[{'label': i, 'value': i} for i in
                                           np.append(['All'], coins['id'].unique())],
                                  value='All',
                                  placeholder='Select the coin'
                                  ),
                     # style={'width': '50%', 'display': 'inline-block'}
                     )
        ),
        dbc.Col(
            dcc.Input(id='coin-money',
                      type='text',
                      placeholder='Enter how much wanna buy',
                      value='0',
                      debounce=True, ),
        ),
        dbc.Col(
            html.Div(id='check-div',
                     style={'display': 'none'}
                     )),

    ]),

    html.Br(),
    dbc.Row(
        dbc.Col(
            html.Button('Submit', id='generate', n_clicks=0),
            width={'size': 10, 'offset': 3}
        ), )

], fluid=True)

app.layout = html.Div(id='parent', children=[navbar, body_app])


@app.callback(Output('check-div', 'children'),
              [Input('coin-buy', 'value'),
               Input('coin-money', 'value')],
              )
def check(coin, money, ):
    money = int(money)
    if coin != 'All' and money > 0:
        df = select_coins(coin)
        df_price = df['priceUsd'][0]
        if df_price < money:
            send_mail(coin)
            return f'buy {coin}'


@app.callback([Output(component_id='coin-table-output', component_property='children'),
               Output('coin-graph', 'children'), ],
              [Input(component_id='coin-dropdown', component_property='value')])
def table_country(coin):
    columns = ['id', 'coinrank', 'symbol', 'name', 'priceUsd', 'dt']
    coins.sort_values(['coinrank', 'dt'], ascending=[True, False], inplace=True)
    if coin == 'All':
        df_final = coins.sort_values('dt', ascending=False).drop_duplicates(subset=['coinrank'],
                                                                            keep='first').sort_values('coinrank')
    else:
        df_final = coins.loc[coins['id'] == '{}'.format(coin)]

    table = dash_table.DataTable(
        data=df_final[columns].to_dict('records'),
        columns=[{'id': c, 'name': c} for c in columns],
        fixed_rows={'headers': True},

        sort_action='native',

        style_table={
            'maxHeight': '450px'
        },

        style_header={'backgroundColor': 'rgb(224,224,224)',
                      'fontWeight': 'bold',
                      'border': '4px solid white',
                      'fontSize': '12px'
                      },

        style_data_conditional=[

            {
                'if': {'row_index': 'odd',
                       },
                'backgroundColor': 'rgb(240,240,240)',
                'fontSize': '12px',
            },

            {
                'if': {'row_index': 'even'},
                'backgroundColor': 'rgb(255, 255, 255)',
                'fontSize': '12px',

            },
        ],

        style_cell={
            'textAlign': 'center',
            'fontFamily': 'Times New Roman',
            'border': '4px solid white',
            'maxWidth': '50px',
            'width': '30px',
            'textOverflow': 'ellipsis',

        }

    )

    df_final = coins.loc[coins['id'] == 'bitcoin'] if coin == 'All' else df_final
    coinid = 'bitcoin' if coin == 'All' else coin

    fig = go.Figure(
        data=go.Scatter(x=df_final.dt,
                        y=df_final.priceUsd, line=dict(color='firebrick', width=4),
                        text=df_final.priceUsd,
                        name='name1'
                        ),
    )
    fig.update_layout(title=f'{coinid}',
                      xaxis_title='Time',
                      yaxis_title='Price',
                      # yaxis_tickprefix='$',
                      # yaxis_ticksuffix='M',
                      margin=dict(l=40, r=50, t=60, b=40),
                      )

    card_content4 = [
        dbc.CardBody([
            html.H6('Coin trend', style={'fontWeight': 'Light', 'textAlign': 'center'}),
            dcc.Graph(figure=fig, style={'height': '450px'})

        ])]

    return table, card_content4


if __name__ == "__main__":
    send_mail_time = 0
    app.run_server()
