import datetime
import dash
from dash.dependencies import Input, Output
from collections import deque
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

url = "https://www.coronavirus2020.kz/"
def parse_data():
	uClient = uReq(url)
	page_html = uClient.read()
	uClient.close()

	page_soup = soup(page_html, "html.parser")

	containers = page_soup.findAll("div", {"class":"city_cov"})

	out_filename = "covid_cases.csv"
	headers = "city, number_of_cases \n"

	f = open(out_filename, "w")
	f.write(headers)


	for container in containers[:1]:
		in_contaners = container.stripped_strings
		for it in in_contaners:
			it = it.replace(" ", "")
			print(it)
			f.write(it.replace("–", ",")+"\n")
	f.close()

scheduler = BackgroundScheduler()
scheduler.add_job(func=parse_data, trigger="interval", seconds=3)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app = dash.Dash('COVID-19 Graphs')

df1 = pd.read_excel('test1.xlsx')
df2 = pd.read_excel('test2.xlsx')

data_dict = {'Birthday paradox':df1,
'Fatality rate':df2}



app.layout = html.Div([
	
	#First task
    html.Div([
        html.H2('COVID-19 Probability Graphs',
                style={'float': 'left', 
                       }),
        ]),
    dcc.Dropdown(id='covid-data-name',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['Birthday paradox','Fatality rate'],
                 multi=True
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
        id='graph-update',
        interval=100),
	
	#Second task
    html.Div([
        html.H2('Calculate the risk of COVID-19 infection from the Birthday paradox:',
                style={'float': 'left'}),
        ]),
	dcc.Input(id='input1', placeholder='Population size', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input2', placeholder='Number of cases', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	dcc.Input(id='input3', placeholder='Meeting size', type='number', debounce=True, 
		style={'white-space':'pre-line','margin-top':10,'margin-right':800,'width':'500px', 'word-wrap':'break-word'}),
	html.Div(id='output1', style={'margin-top':10,'width':'500px', 'word-wrap':'break-word'}),

	#Third task
	html.Div([
        html.H2('Calculate the risk of COVID-19 infection by considering the fatality rate:',
                style={'float': 'left'}),
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
    style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}
    )

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('covid-data-name', 'value')],
    )

def update_graph(data_names):
    graphs = []
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'

    for data_name in data_names:

        data = go.Scatter(
            x=data_dict[data_name].x,
            y=data_dict[data_name].y,
            name='Scatter',
            mode='lines+markers'
            )

        graphs.append(html.Div(dcc.Graph(
            id=data_name,
            animate=True,
            figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[10,510]),
                                                        yaxis=dict(range=[0,110]),
                                                        #margin={'l':50,'r':1,'t':45,'b':1},
                                                        title='{}'.format(data_name))}
            ), className=class_choice))

    return graphs

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

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
for js in external_css:
    app.scripts.append_script({'external_url': js})




if __name__ == '__main__':
	app.run_server(debug=True)