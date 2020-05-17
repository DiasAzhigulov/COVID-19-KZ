import numpy as np
import pandas as pd

def covid_risk_by_birthday(total_population, potential_covid_cases, meeting_sizes=(0,2000,10)):
    """
    This method calculates the risk probability of having at least one COVID-19 infected
    person in meetings of GIVEN SIZES. The algorithm is based on Birthday paradox problem,
    and the algorithm was shared by 
    https://medium.com/@jensensunny/what-is-the-chance-of-meeting-a-covid-19-infected-person-in-grocery-stores-3ca7357fafb2
    and modified by @qasymjomart

    Inputs:
    - total_population - total number of population in the society
    - potential_covid_cases - potential covid cases (not actual, but you can assume actual*1.25)
    - meeting_sizes - meeting sizes range to calculate, type tuple. 
    E.g. (start, end, step_size) implies calculate all risk probabilities for meeting sizes
    from start to end, divide by step_size. Default is (10, 500, 10).

    Return:
    - xs - x-axis value to plot (meeting sizes)
    -probs - prabibility values in percentage for meeting size is xs
    """
    p = 1
    probs = []
    xs = []
    for ii in range(meeting_sizes[0], meeting_sizes[1]+meeting_sizes[2], meeting_sizes[2]):
      for jj in range(ii):
        p = p*((total_population-jj-potential_covid_cases)/total_population)
      probs.append(round((1-p)*100, 4))
      xs.append(ii)

    df = pd.DataFrame({'x': xs, 'y1': probs})

    return df

def covid_risk_by_fatality(num_people_in_area_of_death, total_deaths_today, num_of_employees=np.arange(0,2010,10), fatality_rate=0.0087,
                            days_from_inf_to_death=17.3, doubling_time=6.18):
  


    """
    This method calculates the risk probability of having at least one COVID-19 infected
    person in a meeting of given sizes. The algorithm tales into account the mortality rate;
    it  was suggested by 
    https://public.tableau.com/profile/center.for.social.research#!/vizhome/COVID-19pandemicanimationsandratios/Meetingriskcalculator
    and modified by @irina.dolzhikova

    Inputs:

    num_of_employees=np.arange(10, 500, step_size)
    risk_to_take - 
    total_deaths_today - 
    fatality_rate - 
    days_from_inf_to_death - 
    doubling_time - 
    num_people_in_area_of_death - 
    Return:

    """
    num_times_cases_doubled=days_from_inf_to_death/doubling_time
    num_cases_caused_death=total_deaths_today/fatality_rate

    true_cases_today=num_cases_caused_death*np.power(2, num_times_cases_doubled)
    cur_infect_rate=true_cases_today/num_people_in_area_of_death
    none_has_covid=np.power((1-cur_infect_rate), num_of_employees)
    df = pd.DataFrame({'y2':  (1-none_has_covid)*100})

    return df 

