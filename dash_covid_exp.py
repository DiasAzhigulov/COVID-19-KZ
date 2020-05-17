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
scheduler.add_job(func=pr.parse_data, trigger="interval", seconds=3)
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



external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
app = dash.Dash('COVID-19 Graphs',
                external_scripts=external_js,
                external_stylesheets=external_css)





app.layout = html.Div([
	
	#First task
    html.Div([
        html.H2('COVID-19 Probability Graphs',
                style={'float': 'left', 'font-size':30
                       }),
        ]),
    dcc.Dropdown(id='covid-city',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 placeholder="Select a city",
                 multi=True
                 ),

    html.Div(children=html.Div(id='graph1'), className='row'),
    dcc.Interval(
        id='graph-update1',
        interval=100000000,
        n_intervals=0),

    #Second task
    html.Div([
        html.H2('Calculate the risk of COVID-19 infection from the Birthday paradox:',
                style={'float': 'left', 'font-size':30}),
        ]),
    dcc.Input(id='input1', placeholder='Population size', type='number', debounce=True, 
        style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
    dcc.Input(id='input2', placeholder='Number of cases', type='number', debounce=True, 
        style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
    dcc.Input(id='input3', placeholder='Meeting size', type='number', debounce=True, 
        style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
    html.Div(id='output1', style={'margin-top':10,'width':'500px', 'word-wrap':'break-word'}),

    html.Div(children=html.Div(id='graph2'), className='row'),
    dcc.Interval(
        id='graph-update2',
        interval=100000000,
        n_intervals=0),
    
	#Third task
	html.Div([
        html.H2('Calculate the risk of COVID-19 infection by considering the fatality rate:',
                style={'float': 'left', 'font-size':30}),
        ]),
	dcc.Input(id='input4', placeholder='Number of employees', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input5', placeholder='Total deaths today', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input6', placeholder='Fatality rate', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input7', placeholder='Days from infection to death', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input8', placeholder='Doubling time', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input9', placeholder='Number of people in the area of death', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	html.Div(id='output2', style={'margin-top':10,'margin-bottom':100,'width':'500px', 'word-wrap':'break-word'})
    ], className="container",
    style={'width':'98','margin-left':10,'margin-right':10,'max-width':50000}
    )

@app.callback(
    dash.dependencies.Output('graph1','children'),
    [dash.dependencies.Input('covid-city', 'value')],
    )

def update_birthday(data_names):

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
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'

    try:
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
                figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[10,510]),
                                                            yaxis=dict(range=[0,110]),
                                                            #margin={'l':500,'r':1,'t':45,'b':1},
                                                            title='{}'.format(data_name))}
                ), className=class_choice))

        return graphs
    except:
        return ""

@app.callback(
    dash.dependencies.Output('graph2','children'),
    [dash.dependencies.Input('covid-city', 'value')],
    )

def update_fatality(data_names):

    graphs = []
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'
    
    try:
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
                figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[10,510]),
                                                            yaxis=dict(range=[0,110]),
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
		return "Probability according to the Birthday paradox = "+str(prob)+"%"
	except:
		return "Error! Please fill in all the inputs."

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
		return "Probability with the fatality rate considered = "+str(round(((1-none_has_covid)*100),4))+"%"
	except:
		return "Error! Please fill in all the inputs."


if __name__ == '__main__':
	app.run_server(debug=True)