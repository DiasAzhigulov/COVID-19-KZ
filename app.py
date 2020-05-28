import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import Backend as be
import plotly.graph_objs as go
import Parser_updated as pr
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

scheduler_parser = BackgroundScheduler()
scheduler_parser.add_job(func=pr.parse_data, trigger="interval", seconds=4)
scheduler_parser.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler_parser.shutdown())



# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']


def load_data():
    global df
    df = pd.read_csv("out.csv", sep="\n")


load_data()
scheduler_loader = BackgroundScheduler()
scheduler_loader.add_job(func=load_data, trigger="interval", seconds=3)
scheduler_loader.start()
atexit.register(lambda: scheduler_loader.shutdown())


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([

    #First task
    html.Div([
        html.H2('COVID-19 risk calculator for Kazakhstan and the world',
                style={'position':'relative','text-align':'center','top':'50%','transform':'translate(0%,-50%)','font-size':30,'color':'rgb(255,255,255)'
                       }),
        ],style={'background-color':'#0C4142','margin-left':'0%','margin-right':'0%','margin-top':'0%','height':'10%'}),

    html.Div([html.H6('\n\nThis calculator estimates the probability of at least one person having COVID-19 among a community of certain size. '+
        'Two methods for calculation of the probability, namely Birthday Paradox problem based and Fatality Rate based approaches, are presented. '+
        'This calculator could be valuable for assessing the risk of exposure to COVID-19 in meetings with different number of people, supermarkets, restaurants, and other public places. '+
        'Using this tool, meeting organizers and managers can decide what meeting size to choose to minimize the risk of COVID-19. '+
        'It also provides the graphs for various meeting sizes (user can enter his/her own city) and is specifically adapted for Kazakhstan cities. '
        )], style={'text-align':'center','margin-top':50,'margin-left':10,'margin-right':10}),

    html.Div([html.H6('NOTE:  Please keep in mind that this is a pure statistical calculation based on the publically available data. The real risk of being infected by COVID-19 could drastically alter from the presented calculations. Please interpret the results with caution.')], style={'color':'rgb(255,0,0)','text-align':'center','margin-top':10}),

    #html.H5('Select your city:',style={'text-align':'left','position':'absolute','top':'43.4%','left':'11.2%'}),
    #html.Label(['Select your city'],style={'position':'relative','margin-top':50}),
    html.Div([html.H5('Select your city:'), dcc.Dropdown(
        id='city-dropdown',
        options=[
            {'label': i[0].split(',')[0], 'value': i[0]} for i in df.values
        ],
        value = df.values[0][0]
    )], style={'position':'relative','margin-top':50,'margin-bottom':50,'margin-left':'20%','margin-right':'20%'}),

    #html.Div([], style={'text-align':'center','margin-top':50}),

    html.Div([html.H5(['Select your community size (range):']),dcc.RangeSlider(
                id='slider',
                min=0,
                max=2000,
                step=10,
                marks={
                    0: '0',
                    500: '500',
                    1000: '1000',
                    1500: '1500',
                    2000: '2000',
                    #5000: '5000',
                    #6000: '6000',
                    #7000: '7000',
                    #8000: '8000',
                    #9000: '9000',
                    #10000: '10000',
                },
                value=[0, 400]
            )], style={'position':'relative','margin-top':50,'margin-bottom':50,'margin-left':'20%','margin-right':'20%'}),

    #html.H5(['Select your meeting size (range):'],style={'text-align':'left','position':'absolute','top':'51.1%','left':'2.5%'}),

    html.Div([html.H5('Select your method of risk estimation')], style={'text-align':'center','margin-top':50}),

    html.Div([

        dcc.Tabs(id='tabs-probability-types', value='tab-birthday-paradox', children=[
            dcc.Tab(label='Birthday paradox based estimation', value='tab-birthday-paradox', children=[
                    html.Div(className='three columns', children=[
                        #html.P(["Population size"],style={'position':'absolute','top':'18%','left':'3.4%','fontWeight':'bold'}),
                        html.Div(className='row',children=[
                            html.P(["Population size"], style={'fontWeight':'bold'}),
                            dcc.Input(id="input-population-birtday", type="number", placeholder="Population size", value=''),
                            ], style={'margin-left':10,'margin-top':'5%'}),
                        #html.P(["Number of covid cases"],style={'position':'absolute','top':'29%','left':10,'fontWeight':'bold'}),
                        html.Div(className='row',children=[
                             html.P(["Number of confirmed cases"], style={'fontWeight':'bold'}),
                             dcc.Input(id="input-covid", type="number", placeholder="Number of covid cases", value=''),
                             ], style={'margin-left':10,'margin-top':'5%'}),

                        html.Div(['This method for calculation is based on the idea of Birthday Paradox Problem, which calculates the probability of two people sharing the same birthday within a small community. '+ 
                                'The design for calculation of probability of at least one COVID-19 infection in the room is inspired by the tool by Dr. Jensen Sun [1].'],style={'margin-left':10,'margin-top':50}),

                    ]),
                    html.Div(className='nine columns', children=[
                        dcc.Loading(className='dashbio-loading', children=html.Div(children=html.Div(id='graph-birtday-paradox'), className='row'), 
                            style={'margin-top':50}),
                        dcc.Interval(
                            id='graph-update1',
                            interval=100,
                            n_intervals=0), 
                       ]),

                ]),

            dcc.Tab(label='Fatality rate based estimation', value='tab-fatality-rate', children=[
                    html.Div(className='three columns', children=[
                        #html.P(["Population size"],style={'position':'absolute','top':'18%','left':'3.4%','fontWeight':'bold'}),
                        html.Div(children=[
                            html.P(["Population size"], style={'fontWeight':'bold'}),
                            dcc.Input(id="input-population-fatality", type="number", placeholder="Population size", value=''),
                            ], style={'margin-left':10,'margin-top':'5%'}),

                        #html.P(["Number of fatal cases"],style={'position':'absolute','top':'29%','left':15,'fontWeight':'bold'}),
                        html.Div(children=[
                            html.P(["Number of fatal cases"], style={'fontWeight':'bold'}),
                            dcc.Input(id="input-death", type="number", placeholder="Total death today", value=''),
                            ], style={'margin-left':10,'margin-top':'5%'}),

                        html.Div(['The calculations in this method are based on fatality rate estimation, which is the percentage of people who had been infected with the coronavirus and then died. '+
                                'Fatality rate is the most important aspect that defines whether a disease brings worldwide attention and has a potential to cause a pandemic [2]. '+
                                'Thus, such a method is considered to be more reliable and should be used if there is available information regarding the deaths in the local area. '+
                                'This tool is inspired by the article of Tomas Pueyo [3] with the calculations being presented in [4].'],style={'margin-left':10,'margin-top':50})#, 
                                # style={'font-size':16,'position':'relative','margin-left':'20%','margin-right':'20%','margin-top':10}),
                    ]),
                    html.Div(className='nine columns', children=[
                        dcc.Loading(className='dashbio-loading', children=html.Div(children=html.Div(id='graph-fatality-rate'), className='row'), 
                            style={'margin-top':50}),
                        dcc.Interval(
                            id='graph-update2',
                            interval=100,
                            n_intervals=0), 
                        ]),
                ]),
        ]),

    ], style={'position':'relative','margin-top':50}),


    html.Div([html.H4('Interpretation of the estimates [1]:', style={'fontWeight':'bold'})], style={'margin-top':50,'margin-left':10,'margin-right':10}),
    html.Div([html.Ul([html.Li('0-25%: Relatively safe. However, keep social distancing principle and wear mask;'),
                    html.Li('25-50%: Relatively serious. It is very important to wear masks and gloves;'),
                    html.Li('50-75%: Risky. Make sure you wear masks, gloves, eye protectors. Avoid any touches;'),
                    html.Li('>75%: Very risky. Unless there is absolute need to go out, stay at home. Use all of the possible protective means. Avoid any contact.')],
                    style={'list-style-type':'disc','font-size':16})], style={'margin-left':10,'margin-right':10}),

    html.Div([html.H4('References', style={'fontWeight':'bold'})], style={'margin-left':10,'margin-right':10}),
    html.Div(['[1] ',dcc.Link('zihengsun.github.io/covid.html',href='https://zihengsun.github.io/covid.html',target='_blank')], style={'font-size':16,'margin-left':10,'margin-right':10}),
    html.Div(['[2] Wang, L., Li, J., Guo, S., Xie, N., Yao, L., Cao, Y., ... & Ji, J. (2020). Real-time estimation and prediction of mortality caused by COVID-19 with patient information based algorithm. Science of the Total Environment, 138394.'], style={'font-size':16,'margin-left':10,'margin-right':10}),
    html.Div(['[3] ',dcc.Link('medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca',href='https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca',target='_blank')], style={'font-size':16,'margin-left':10,'margin-right':10}),    
    html.Div(['[4] ',dcc.Link('docs.google.com/spreadsheets/d/17YyCmjb2Z2QwMiRRwAb7W0vQoEAiL9Co0ARsl03dSlw/edit#gid=1919103833',href="https://docs.google.com/spreadsheets/d/17YyCmjb2Z2QwMiRRwAb7W0vQoEAiL9Co0ARsl03dSlw/edit#gid=1919103833",target='_blank')], style={'font-size':16,'margin-left':10,'margin-right':10}),        
    
    html.Div([html.H4('Acknowledgements', style={'fontWeight':'bold'})], style={'margin-left':10,'margin-right':10}),
    html.Div(['This work was performed by students and professors of ',dcc.Link('Nazarbayev University',href='https://nu.edu.kz',target='_blank'),': Dias Azhigulov, Islambek Temirbek, Irina Dolzhikova, Kassymzhomart Kunanbayev, Prof. Amin Zollanvari, and Prof. Antonio Sarria-Santamera. '+
        'The authors would like to acknowledge the support of NPO Young Researchers Alliance and Nazarbayev University Corporate Fund “Social Development Fund” for grant under their Fostering Research and Innovation Potential Program.'], 
        style={'margin-bottom':100,'font-size':16,'margin-left':10,'margin-right':10}),
    
    ], className="container",
    style={'width':'100%','height':'100%','position': 'absolute', 'top': 0, 'left': 0,'max-width':50000}
    )


@app.callback(
    [dash.dependencies.Output('input-population-birtday', 'value'),
    dash.dependencies.Output('input-covid', 'value'),
    dash.dependencies.Output('input-population-fatality', 'value'),
    dash.dependencies.Output('input-death', 'value')],
    [dash.dependencies.Input('city-dropdown', 'value')])

def update_inputs(value):
    df1 = pd.read_csv("out.csv")
    return int(value.split(',')[1]),  int(value.split(',')[2]), int(value.split(',')[1]), int(value.split(',')[3].split('.')[0])


@app.callback(
    dash.dependencies.Output('graph-birtday-paradox','children'),
    [dash.dependencies.Input('slider', 'value'),
    dash.dependencies.Input('input-population-birtday', 'value'),
    dash.dependencies.Input('input-covid', 'value')]
    )
def update_birthday_graph(meeting_size, population_number, covid_number):

    df1 = pd.read_csv("out.csv")

    if population_number in df1['population'].values and population_number != 1000000:
        title = df1['city'][be.getIndexes(df1, population_number)[0]]
    else:
        title = ""
    try:
        data_plot = be.covid_risk_by_birthday(population_number, covid_number)
        # print(data_plot)
        data = go.Scatter(
                    x=data_plot.x,
                    y=data_plot.y,
                    name='Scatter',
                    mode='lines+markers'
                    )

        print("\n\n\n"+title+"\n\n\n")
        return  html.Div(dcc.Graph(
                    id=title,
                    animate=True,
                    figure={'data': [data] ,'layout' : go.Layout(xaxis={'title':'Community size','range': meeting_size},
                                                               yaxis={'title':'Probability of having at least one COVID-19 case'},
                                                               title=title)
                                                                }
                    ))
    except:
        return ""

@app.callback(
    dash.dependencies.Output('graph-fatality-rate','children'),
    [dash.dependencies.Input('slider', 'value'),
    dash.dependencies.Input('input-population-fatality', 'value'),
    dash.dependencies.Input('input-death', 'value')]
    )
def update_fatality_graph(meeting_size, population_number, covid_fatal_number):
    
    df1 = pd.read_csv("out.csv")
    #df2 = pd.read_csv("fatality_rate_updated.csv"))

    if population_number in df1['population'].values and population_number != 1000000:
        title = df1['city'][be.getIndexes(df1, population_number)[0]]
    else:
        title = ""
    try:

        data_plot = be.covid_risk_by_fatality(population_number, covid_fatal_number)
        # print(data_plot)
        data = go.Scatter(
                    x=data_plot.x,
                    y=data_plot.y,
                    name='Scatter',
                    mode='lines+markers'
                    )
        print("\n\n\n"+title+"\n\n\n")
        return  html.Div(dcc.Graph(
                    id=title,
                    animate=True,
                    figure={'data': [data] ,'layout' : go.Layout(xaxis={'title':'Community size','range': meeting_size},
                                                               yaxis={'title':'Probability of having at least one COVID-19 case'},
                                                               title=title)
                                                                }
                    ))
    except:
        return ""





if __name__ == '__main__':
    app.run_server(debug=True)