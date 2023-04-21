from jobs import q, update_job_status, get_redis_client

@q.worker
def execute_job(jid):
    jobs.update_job_status(jid, 'in progress')
    rd_jobs = jobs.get_redis_client(7)
    job = rd_jobs.hgetall(jid)
    if job['type'] == 'efficiencyCalculator':
        efficiencyCalculator(job['param'])
    elif job['type'] == 'graph':
        graph(job['param'])
    jobs.update_job_status(jid, 'complete')

def efficiencyCalculator(city: str):
    efficiencies = {}
    rd_solar = jobs.get_redis_client(0)
    for panelType in rd_solar.hkeys():
        rd_weather = jobs.get_redis_client(cities[city])
        solarPower = 0
        for date in rd.keys():
            efficiency = rd_solar.hget(panelType, "Efficiency")
            t_coeff = rd_solar.hget(panelType, "T_Coeff")
            weatherData = rd_weather.hgetall(date)
            temperature = weatherData["temp"]
            sunsetEpoch = weatherData["sunsetEpoch"]
            sunriseEpoch = weatherData["sunriseEpoch"]
            cloudCover = weatherData["cloudcover"]
            solarPower += efficiency * (1 + (temperature - 25) * t_coeff / 100) * (100 - cloudCover) / 100 * ((sunsetEpoch - sunriseEpoch) / 86400)
        efficiencies[panelType] = solarPower
    rd_job = jobs.get_redis_client(7)
    rd_job.hset('efficiencies', mapping = efficiencies)

def graph(category: str):
    return 'yo'
