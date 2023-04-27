import jobs
from hotqueue import HotQueue
from datetime import datetime
import matplotlib.pyplot as plt
import json

q = jobs.get_hotqueue()

def getCities() -> dict:
    """
    returns the list of cities in the weather data
    """
    cities = {'Dallas': 1, 'Austin': 2, 'Houston': 3, 'San_Antonio': 4}
    return cities

@q.worker
def execute_job(jid: str):
    """
    Runs each time a job is added to the hotqueue. Checks the type of the job and runs the corresponding function.
    """
    jobs.update_job_status(jid, 'in progress')
    jobType = jobs.get_job_type(jid)
    jobParam = jobs.get_job_param(jid)
    if jobType == 'graphEfficiency':
        graphEfficiency(jid, jobParam)
    elif jobType == 'graphWeather':
        graphWeather(jid, jobParam)
    else:
        jobs.update_job_status(jid, 'Error: job type does not exist')
       
def graphEfficiency(jid: str, city: str):
    """
    Graphs the solar panel efficiency vs time for the given city and uploads the image to redis.
    """
    efficiencies = {}
    rd_solar = jobs.get_redis_client(0)
    if rd_solar.keys == []:
        jobs.update_job_status(jid, 'Error, data has not been loaded into the database')
        return 0
    cities = getCities()
    time_values = {}
    y_values = {}
    for panelType in rd_solar.keys():
        rd_weather = jobs.get_redis_client(cities[city])
        start_time = int(rd_weather.hget('2023-01-01', 'datetimeEpoch'))
        solarPower = 0
        time_values[panelType] = []
        y_values[panelType] = []
        dates = list(rd_weather.keys())
        dates.sort()
        for date in dates:
            efficiency = float(rd_solar.hget(panelType, "Efficiency"))
            t_coeff = float(rd_solar.hget(panelType, "T_Coeff"))
            weatherData = rd_weather.hgetall(date)
            temperature = float(weatherData["temp"])
            sunsetEpoch = int(weatherData["sunsetEpoch"])
            sunriseEpoch = int(weatherData["sunriseEpoch"])
            cloudCover = float(weatherData["cloudcover"])
            datetime = int(weatherData['datetimeEpoch'])
            solarPowerCalc = efficiency * (1.0 + (temperature - 5.0) * t_coeff) * (100.0 - cloudCover) / 100.0 * ((sunsetEpoch - sunriseEpoch) / 86400)
            y_values[panelType].append(solarPowerCalc)
            day = ((datetime - start_time) / 86400)
            time_values[panelType].append(day)
            solarPower += solarPowerCalc
        efficiencies[panelType] = solarPower

    bestSolarPanel = max(efficiencies, key=efficiencies.get)
    for panelType in y_values.keys():
        plt.plot(time_values[panelType], y_values[panelType], label = panelType)

    plt.ylabel('Relative Efficiency')
    plt.xlabel('Days since 01-01-2023')
    plt.title('Efficiency vs Day of the Year')
    plt.legend()
    plt.text(1.1, 0.11, f'{bestSolarPanel} was the Most Efficient Type', fontsize=10) 
    plt.savefig('plot.png')
    file_bytes = open('plot.png', 'rb').read()

    jobs.update_job_results(jid, file_bytes)
    jobs.update_job_status(jid, 'complete')
    jobs.update_job_end(jid)

    plt.clf()    

def graphWeather(jid: str, params: str):
    """
    Graphs the weather data vs time for the given category of data and for the given city
    """
    params = json.loads(params)
    city = params['city']
    cities = getCities()
    category = params['category']
    rd_weather = jobs.get_redis_client(cities[city])
    if rd_weather.keys == []:
        jobs.update_job_status(jid, 'Error, data has not been loaded into the database')
        return 0
        
    graph_data = {}
    time_values = []
    y_values = []
    start_time = int(rd_weather.hget('2023-01-01', 'datetimeEpoch'))
    for date in rd_weather.keys():
        day = ((int(rd_weather.hget(date, 'datetimeEpoch')) - start_time) / 86400)
        time_values.append(day)
        y_value = float(rd_weather.hget(date, category))
        y_values.append(y_value)
    plt.plot(time_values, y_values)
    plt.ylabel(category)
    plt.xlabel('Days since 01-01-2023')
    plt.title(f'{category} vs Time')
    plt.savefig('plot.png')
    file_bytes = open('plot.png', 'rb').read()

    jobs.update_job_results(jid, file_bytes)
    jobs.update_job_status(jid, 'complete')
    jobs.update_job_end(jid)
    
if __name__ == '__main__':
    execute_job()
