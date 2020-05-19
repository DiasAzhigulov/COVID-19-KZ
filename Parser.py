from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import time
import atexit
from transliterate import translit, get_available_language_codes
from apscheduler.schedulers.background import BackgroundScheduler

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
			print(it)
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
			print(it)
			# print(translit(it, 'ru', reversed=True))
			it = translit(it, 'ru', reversed=True)
			f.write(it.replace("–", ",")+"\n")
	f.close()


# if __name__== '__main__':
# 	parse_data()