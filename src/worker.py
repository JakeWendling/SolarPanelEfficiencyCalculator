import jobs
from hotqueue import HotQueue
from datetime import datetime
import matplotlib.pyplot as plt
import json

q = jobs.get_hotqueue()

def getCities() -> dict:
    cities = {'Dallas': 1, 'Austin': 2, 'Houston': 3, 'San_Antonio': 4}
    return cities

@q.worker
def execute_job(jid):
    jobs.update_job_status(jid, 'in progress')
    jobType = jobs.get_job_type(jid)
    jobParam = jobs.get_job_param(jid)
    if jobType == 'efficiency':
        efficiencyCalculator(jid, jobParam)
    elif jobType == 'graph':
        graph(jid, jobParam)
    else:
        jobs.update_job_status(jid, 'Error: job type does not exist')
       
def efficiencyCalculator(jid: str, city: str):
    efficiencies = {}
    rd_solar = jobs.get_redis_client(0)
    if rd_solar.keys == []:
        jobs.update_job_status(jid, 'Error, data has not been loaded into the database')
        return 0
    cities = getCities()
    for panelType in rd_solar.keys():
        rd_weather = jobs.get_redis_client(cities[city])
        solarPower = 0
        for date in rd_weather.keys():
            efficiency = float(rd_solar.hget(panelType, "Efficiency"))
            t_coeff = float(rd_solar.hget(panelType, "T_Coeff"))
            weatherData = rd_weather.hgetall(date)
            temperature = float(weatherData["temp"])
            sunsetEpoch = int(weatherData["sunsetEpoch"])
            sunriseEpoch = int(weatherData["sunriseEpoch"])
            cloudCover = float(weatherData["cloudcover"])
            solarPower += efficiency * (1.0 + (temperature - 25.0) * t_coeff) * (100.0 - cloudCover) / 100.0 * ((sunsetEpoch - sunriseEpoch) / 86400)
        efficiencies[panelType] = solarPower
    jobs.update_job_results(jid, json.dumps(efficiencies))
    jobs.update_job_status(jid, 'complete')
    jobs.update_job_end(jid)

def graph(jid: str, params: str):
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
