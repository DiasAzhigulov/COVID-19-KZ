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

    df = pd.DataFrame({'x': xs, 'y': probs})

    return df


def covid_risk_by_fatality(num_people_in_area_of_death, total_deaths_today, num_of_employees=np.arange(0,2010,10), fatality_rate=0.0087,
                            days_from_inf_to_death=17.3, doubling_time=6.18):
  

    population_number = num_people_in_area_of_death
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

    df1 = pd.read_csv("params.csv")
    df2 = pd.read_csv("out.csv")   
    if population_number in df2['population'].values and population_number != 1000000:
        fatality_rate = df1['fatality_rate'][getIndexes(df2, population_number)[0]]
        doubling_time = df1['doubling_time'][getIndexes(df2, population_number)[0]]
        print("\n\n\n Fatality rate = " + str(fatality_rate))
        print("Doubling time = " + str(doubling_time) + "\n\n\n")
    else:
        fatality_rate=0.0087
        doubling_time=6.18

    num_times_cases_doubled=days_from_inf_to_death/doubling_time
    num_cases_caused_death=total_deaths_today/fatality_rate

    true_cases_today=num_cases_caused_death*np.power(2, num_times_cases_doubled)
    cur_infect_rate=true_cases_today/num_people_in_area_of_death
    none_has_covid=np.power((1-cur_infect_rate), num_of_employees)
    df = pd.DataFrame({'x':num_of_employees, 'y':  (1-none_has_covid)*100})

    return df 


def getIndexes(dfObj, value):
        ''' Get index positions of value in dataframe i.e. dfObj.'''
        listOfPos = list()
        # Get bool dataframe with True at positions where the given value exists
        result = dfObj.isin([value])
        # Get list of columns that contains the value
        seriesObj = result.any()
        columnNames = list(seriesObj[seriesObj == True].index)
        # Iterate over list of columns and fetch the rows indexes where value exists
        for col in columnNames:
            rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append(row)
        # Return a list of tuples indicating the positions of value in the dataframe
        return listOfPos