from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import time
# import atexit
from transliterate import translit, get_available_language_codes
import pandas as pd
# from apscheduler.schedulers.background import BackgroundScheduler

def parse_data():
	url = "https://www.coronavirus2020.kz/"

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
			#print(it)
			# print(translit(it, 'ru', reversed=True))
			it = translit(it, 'ru', reversed=True)
			f.write(it.replace("–", ",")+"\n")
	f.close()


	out_filename = "covid_fatal_cases.csv"
	headers = "city, number_of_fatal_cases \n"
	f = open(out_filename, "w")
	f.write(headers)

	for container in containers[-1:]:
		in_contaners = container.stripped_strings
		for it in in_contaners:
			it = it.replace(" ", "")
			# print(it)
			# print(translit(it, 'ru', reversed=True))
			it = translit(it, 'ru', reversed=True)
			f.write(it.replace("–", ",")+"\n")
	f.close()
	df_covid = pd.read_csv("covid_cases.csv", skiprows=[0], names=['city', 'number_of_cases'])
	df_pop = pd.read_csv("population_size.csv", skiprows=[0], names=['city', 'population'])
	df_fatal = pd.read_csv("covid_fatal_cases.csv", skiprows=[0], names=['city', 'number_of_fatal_cases'])
	df = pd.merge(df_covid, df_fatal, how='left').replace(float('nan'), 0)
	df.drop('city', axis=1, inplace=True)
	df = pd.concat([df_pop, df], axis=1)
	df['number_of_cases'] = df['number_of_cases'].apply(lambda x: (int(x.split('(+')[0]) + int(x.split('(+')[1].split(')')[0])) if '+' in str(x) else int(x))
	df = df.append({'city':'Enter your own city','population':1000000, 'number_of_cases': 0, 'number_of_fatal_cases': 0},ignore_index=True)
	df.to_csv('out.csv', index=False)
