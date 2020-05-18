import datetime
import dash
from dash.dependencies import Input, Output
from collections import deque
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import Backend as be
import Parser as pr
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from transliterate import translit, get_available_language_codes


scheduler = BackgroundScheduler()
scheduler.add_job(func=pr.parse_data, trigger="interval", seconds=300)
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


df_covid = pd.read_csv("covid_cases.csv")
df_pop = pd.read_csv("population_size.csv")
array_df = []
num_death_today = 2 #ASSUMED
data_dict = {}
num_city = 17

for i in range(num_city):    
    df1 = be.covid_risk_by_birthday(df_pop['population'][i],df_covid[' number_of_cases '][i])
    df2 = be.covid_risk_by_fatality(df_pop['population'][i],num_death_today)
    df = pd.concat([df1,df2], axis=1, sort=False)
    array_df.append(df)
    data_dict[df_pop['city'][i]] = df



# external_css = ["https://cdnjs.cloduflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
external_css = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
# external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
app = dash.Dash('COVID-19 Graphs',
                # external_scripts=external_js,
                external_stylesheets=external_css)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(id='alignment-body', className='row', children=[
    html.Div( className='row', children=[
        html.H2('COVID-19 Probability Graphs for Kazakhstan',
                style={'float': 'left', 'font-size':30}),
        ]),



    html.Div(id='covid-control-tabs', className='three columns', children=[

        html.Div(className='eleven columns', children=[


            dcc.Tabs( id = 'Tabs', value = 'what-is', children = [ 

                dcc.Tab(
                    label='About',
                    value='what-is',
                    children=html.Div(className='control-tab', children=[
                        html.H5(
                            className='what-is',
                            children='COVID-19 Risk Estimator Based on Birthday Paradox Problem',
                            style={'font-size':18}
                        ),
                        # html.P(
                        #     html.Ul(
                        #         html.Li("""0-25%: Relatively safe. However, keep social distancing principle and wear mask;"""),
                        #         html.Li("""25-50%: Relatively serious. It is very important to wear masks and gloves;"""),
                        #         html.Li("""50-75%: Very risky. Make sure you wear masks, gloves, eye protectors. Avoid any touches;"""),
                        #         html.Li(""" >75%: Highly risky; unless there is absolute need to go out, stay at home. Use all of the possible protective means; avoid any contact.""")                                )
                        # ),

                        html.P(
                            """
                            Inspired by the idea of Birthday Paradox Problem to calculate the probability of two people sharing the same birthday within a small community, this calculator estimates the probability of at least one person having COVID-19 among a community of certain size. 

                            Therefore, this calculator could be of value for assessing the risk of exposure to COVID-19 in various-sized meetings, supermarkets, restaurants, and other public places. Using this tool, meeting organizers and managers can decide what meeting size to choose to minimize the risk of contagious COVID-19.

                            The design is inspired from the tool by Dr. Jensen Sun [1]. However, this calculator builds the graph for different meeting sizes, and, although not necessarily, but specifically adapted for Kazakhstan cities.

                            """,
                            style={'font-size':10}
                        ),
                        html.H5(children='COVID-19 Risk Calculator using fatality rate',
                            style={'font-size':18}),

                        html.P(
                            """
                            The calculations in this method are based on fatality rate estimation, which is the percentage of people who had been infected with the coronavirus and then died. Fatality rate is the most important aspect that defines whether a disease brings world-wide attention and has a potential to cause a pandemic [2]. Thus, such a method is considered to be more reliable and should be used if there is available information regarding the deaths in the local area. 

                            This tool is inspired by the article of Tomas Pueyo [3] with the calculations being presented in [4]. 

                            
                            """,
                            style={'font-size':10}
                        ),
                    ])
                ),

                dcc.Tab(label='Birthday paradox', value = 'Birthday-paradox' , children=[

                    #Second task
                    html.Div([
                        html.H5('Calculate the risk of COVID-19 infection from the Birthday paradox:'),
                        ]),
                    dcc.Input(id='input1', placeholder='Population size', type='number', debounce=True),
                    dcc.Input(id='input2', placeholder='Number of cases', type='number', debounce=True),
                    dcc.Input(id='input3', placeholder='Meeting size', type='number', debounce=True),
                    html.Div(id='output1'),

                    ]),

                dcc.Tab(label='Fatality rate', value='Fatality-rate', children=[

                    
                    #Third task
                    html.Div([
                        html.H5('Calculate the risk of COVID-19 infection by considering the fatality rate:'),
                        ]),
                    dcc.Input(id='input4', placeholder='Number of employees', type='number', debounce=True),
                    dcc.Input(id='input5', placeholder='Total deaths today', type='number', debounce=True),
                    dcc.Input(id='input6', placeholder='Fatality rate', type='number', debounce=True),
                    dcc.Input(id='input7', placeholder='Days from infection to death', type='number', debounce=True),
                    dcc.Input(id='input8', placeholder='Doubling time', type='number', debounce=True),
                    dcc.Input(id='input9', placeholder='Number of people in the area of death', type='number', debounce=True),
                    html.Div(id='output2')]),

            ])
        ])
    ]),



    html.Div( id='COVID-19 Probability Graphs', className='eight columns', children=[
    #First task

        html.Div(id='Dropdown-and-Slider', className='row', children=[
            dcc.Dropdown(id='covid-city',
                     options=[{'label': s, 'value': s}
                              for s in data_dict.keys()],
                     placeholder="Select a city",
                     multi=True,
                     value='Nur-Sultan' 
                     #style={'width':1850,'margin-bottom':50}
                     ),


            dcc.RangeSlider(
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
                value=[0, 800]
            ),

        
        
        html.Div(children=html.Div(id='graph1'), className='five columns'),
            dcc.Interval(
                id='graph-update1',
                interval=100,
                n_intervals=0),                
        html.Div(children=html.Div(id='graph2'), className='five columns'),
            dcc.Interval(
                id='graph-update2',
                interval=100,
                n_intervals=0)     
        ])
    ])
])

@app.callback(
    dash.dependencies.Output('graph1','children'),
    [dash.dependencies.Input('slider', 'value'),
    dash.dependencies.Input('covid-city', 'value')],
    )

def update_birthday(val,data_names):

    df_covid = pd.read_csv("covid_cases.csv")
    df_pop = pd.read_csv("population_size.csv")
    array_df = []
    num_death_today = 2 #ASSUMED
    data_dict = {}
    num_city = 17

    for i in range(num_city):    
        df1 = be.covid_risk_by_birthday(df_pop['population'][i],df_covid[' number_of_cases '][i])
        df2 = be.covid_risk_by_fatality(df_pop['population'][i],num_death_today)
        df = pd.concat([df1,df2], axis=1, sort=False)
        array_df.append(df)
        data_dict[df_pop['city'][i]] = df


    graphs = []

    try:
        if len(data_names)>1:
            class_choice = 'col s12 m6 l6'
        else:
            class_choice = 'col s12'
        for data_name in data_names:
            data = go.Scatter(
                x=data_dict[data_name].x,
                y=data_dict[data_name].y1,
                name='Scatter',
                mode='lines+markers'
                )

            graphs.append(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                figure={'data': [data],'layout' : go.Layout(xaxis={'title':'Meeting size','range':val},
                                                            yaxis={'title':'Probability'},
                                                            #margin={'l':500,'r':1,'t':45,'b':1},
                                                            title='{}'.format(data_name))}
                ), className=class_choice))

        return graphs
    except:
        return ""

@app.callback(
    dash.dependencies.Output('graph2','children'),
    [dash.dependencies.Input('slider', 'value'),
    dash.dependencies.Input('covid-city', 'value')],
    )

def update_fatality(val,data_names):

    graphs = []

    try:
        if len(data_names)>1:
            class_choice = 'col s12 m6 l6'
        else:
            class_choice = 'col s12'
        for data_name in data_names:
            data = go.Scatter(
                x=data_dict[data_name].x,
                y=data_dict[data_name].y2,
                name='Scatter',
                mode='lines+markers'
                )

            graphs.append(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                figure={'data': [data],'layout' : go.Layout(xaxis={'title':'Meeting size','range':val},
                                                            yaxis={'title':'Probability'},
                                                            #margin={'l':500,'r':1,'t':45,'b':1},
                                                            title='{}'.format(data_name))}
                ), className=class_choice))

        return graphs
    except:
        return ""    

@app.callback(
	Output(component_id='output1', component_property='children'),
	[Input(component_id='input1', component_property='value'),
	Input(component_id='input2', component_property='value'),
	Input(component_id='input3', component_property='value')])

def update_value_Kassym(total_population, potential_covid_cases, meeting_size):

	try:
		p = 1
		for jj in range(meeting_size):
			p = p*((total_population-jj-potential_covid_cases)/total_population)
		prob = round((1-p)*100, 4)
		return html.H3("Probability according to the Birthday paradox = "+str(prob)+"%")
	except:
		return ""

@app.callback(
	Output(component_id='output2', component_property='children'),
	[Input(component_id='input4', component_property='value'),
	Input(component_id='input5', component_property='value'),
	Input(component_id='input6', component_property='value'),
	Input(component_id='input7', component_property='value'),
	Input(component_id='input8', component_property='value'),
	Input(component_id='input9', component_property='value')])

def update_value_Irina(num_of_employees, total_deaths_today, fatality_rate,
	days_from_inf_to_death, doubling_time, num_people_in_area_of_death):

	try:
		num_times_cases_doubled=days_from_inf_to_death/doubling_time
		num_cases_caused_death=total_deaths_today/fatality_rate

		true_cases_today=num_cases_caused_death*np.power(2, num_times_cases_doubled)
		cur_infect_rate=true_cases_today/num_people_in_area_of_death
		none_has_covid=np.power((1-cur_infect_rate), num_of_employees)
		return html.H3("Probability with the fatality rate considered = "+str(round(((1-none_has_covid)*100),4))+"%")
	except:
		return ""


if __name__ == '__main__':
	app.run_server(debug=True)