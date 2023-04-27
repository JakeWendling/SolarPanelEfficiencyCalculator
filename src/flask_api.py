import requests
import redis
import json
from typing import List
from flask import Flask, request, send_file
import os
import matplotlib.pyplot as plt
import jobs

app = Flask(__name__)

def checkData():
    """
    Checks if the data is loaded

    Returns:
        bool: returns true if the data is loaded, false if it is not loaded
    """
    rd = get_redis_client()
    return len(rd.keys()) > 0 

def get_redis_client(db: int=0, decode: bool=True):
    """
    Gives the redis db object
    
    Args:
        db: (int) database index/page
        decode: (bool) whether to decode byte responses to str
    
    Returns:
        rd: redis object
    """
    redis_ip = os.environ.get('REDIS_IP')
    if not redis_ip:
        raise Exception('Error: Ip not found')
    rd = redis.Redis(host=redis_ip, port=6379, db=db, decode_responses=decode)
    return rd

def getCities() -> dict:
    """
    Returns the list of cities contained in the weather data
    """
    cities = {'Dallas': 1, 'Austin': 2, 'Houston': 3, 'San_Antonio': 4}
    return cities
    
@app.route('/data', methods=['POST'])
def postData() -> dict:
    """
    Gets the weather/solar panel data and saves the data in dictionary format in the flask app.

    Returns:
        string: Message that tells the user that the data has successfuly been obtained
    """
    cities = getCities()
    for i in range(len(cities)):
        city = list(cities.keys())[i]
        with open(f'data/{city}.json', 'r') as f:
            rd = get_redis_client(i+1)
            data = json.load(f)
            for day in data['days']:
                day['stations'] = ', '.join(day['stations'])
                if day['preciptype']:
                    day['preciptype'] = ', '.join(day['preciptype'])
                else:
                    day['preciptype'] = 'none'
                rd.hset(day['datetime'], mapping=day)
    with open(f'data/Solar.json','r') as f:
        rd = get_redis_client(0)
        solarData = json.load(f)
        for panelType in solarData.keys():
            rd.hset(panelType, mapping=solarData[panelType]) 
    return "Data loaded\n"

@app.route('/data', methods=['DELETE'])
def deleteData() -> str:
    """
    Deletes the data stored in the redis db

    Returns:
        string: success message
    """
    rd = get_redis_client()
    rd.flushall()
    return "Data deleted\n"

@app.route('/data', methods=['GET'])
def getData() -> dict:
    """
    Gets the weather/solar data and returns the data in dictionary format

    Returns:
        data: The stored data in dictionary format.
    """
    data = []
    rd_solar = get_redis_client(0)
    for panelType in rd_solar.keys():
        data.append(rd_solar.hgetall(panelType))
    cities = getCities()
    for city in cities.keys():
        rd = get_redis_client(cities[city])
        for date in rd.keys():
            data.append(rd.hgetall(date))
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    return data

@app.route('/cities', methods=['GET'])
@app.route('/weather/cities', methods=['GET'])
def getAllCities() -> List[str]:
    """
    Gets the weather data and returns the list of cities
    
    Returns:
        dateList: a list of cities (strings) for which weather data is available.
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    cities = getCities()
    return ',\n'.join(cities.keys())+'\n'

@app.route('/weather/cities/<city>', methods=['GET'])
def getCityWeatherData(city: str) -> List[dict]:
    """
    Gets the weather data and returns the data for a given city
    
    Returns:
        weatherData: a list of weather data (dictionaries)
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400

    cities = getCities()
    if city not in cities:
        return "Error: City not found. Available cities can be found in /weather/cities.\n", 400
    rd = get_redis_client(cities[city])
    dates = list(rd.keys())
    dates.sort()
    start = request.args.get('start', dates[0])
    end = request.args.get('end', dates[len(dates) - 1])
    if start not in rd.keys():
        return "Invalid start parameter; start must be a valid date in the format YYYY-MM-DD.", 400
    if end not in rd.keys():
        return "Invalid end parameter; end must be a valid date in the format YYYY-MM-DD.", 400
    startIndex = dates.index(start)
    endIndex = dates.index(end)
    weatherData = []
    for date in dates:
        weatherData.append(rd.hgetall(date))
    return weatherData[startIndex:endIndex]

@app.route('/weather/cities/<city>/dates', methods=['GET'])
def getDates(city: str) -> List[str]:
    """
    Gets the weather data and returns the list of dates in a list
    
    Returns:
        dateList: a list of dates (strings) for which weather data is available.
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    cities = getCities()
    if city not in cities:
        return "Error: City not found. Available cities can be found in /weather/cities.\n", 400
    rd = get_redis_client(cities[city])
    dates = rd.keys()
    dates.sort()
    return dates

@app.route('/weather/cities/<city>/dates/<date>', methods=['GET'])
def getWeatherData(city: str, date: str) -> dict:
    """
    Gets the weather data, 
    then returns the weather data for a given date/city, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        date: A string representing a date.
        city: string representing a city.
        
    Returns:
        weatherData: Dictionary containing data from the given date, if available. 
    
    Raises:
        If no weather data is available for the given date/city, 
        returns an error message and a 400 status code.
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    cities = getCities()
    if city not in cities:
        return "Error: City not found. Available cities can be found in /weather/cities.\n", 400
    rd = get_redis_client(cities[city])
    weatherData = rd.hgetall(date)
    if weatherData == {}:
        return "Error: Date not found. Available dates can be found in /weather/cities/<city>/dates \n", 400
    return weatherData

@app.route('/weather/cities/<city>/dates/<date>/categories', methods=['GET'])
@app.route('/weather/categories', methods=['GET'])
def getCategories() -> dict:
    """
    Gets the weather data, 
    then returns the categories for weather data, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        category: string representing category of data to return.
        
    Returns:
        weatherData: Dictionary containing data from the given date, if available. 
    
    Raises:
        If no weather data is available for the given date/city, 
        returns an error message and a 400 status code.
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    cities = getCities()
    city = 'Dallas'
    date = '2023-01-01'
    rd = get_redis_client(cities[city])
    weatherData = rd.hgetall(date)
    return list(weatherData.keys())

@app.route('/weather/cities/<city>/categories/<category>', methods=['GET'])
def getSpecificWeatherData(city: str, category: str) -> dict:
    """
    Gets the weather data, 
    then returns the weather data of a given category for a given city, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        city: string representing a city.
        category: string representing category of data to return.
        
    Returns:
        weatherData: Dictionary containing data from the given date, if available. 
    
    Raises:
        If no weather data is available for the given date/city, 
        returns an error message and a 400 status code.
    """
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    cities = getCities()
    if city not in cities:
        return "Error: City not found. Available cities can be found in /weather/cities.\n", 400
    if not checkCategories(category):
        return "Error: Category not found. Available categories can be found at /weather/categories.\n", 400
    rd = get_redis_client(cities[city])

    dates = list(rd.keys())
    dates.sort()
    start = request.args.get('start', dates[0])
    end = request.args.get('end', dates[len(dates) - 1])
    if start not in rd.keys():
        return "Invalid start parameter; start must be a valid date in the format YYYY-MM-DD.", 400
    if end not in rd.keys():
        return "Invalid end parameter; end must be a valid date in the format YYYY-MM-DD.", 400
    startIndex = dates.index(start)
    endIndex = dates.index(end)

    weatherData = {}
    dates = rd.keys()
    dates.sort()
    for dateIndex in range(startIndex, endIndex + 1):
        date = dates[dateIndex]
        weatherData[date] = rd.hget(date, category)
    return weatherData

def checkCategories(category: str):
    """
    Checks if the given category exists in the data

    Returns:
        True: if the category exists
        False: if the category was not found
    """
    rd = get_redis_client(1)
    date = '2023-01-01'
    weatherData = rd.hgetall(date)
    return category in weatherData.keys()

@app.route('/solar', methods=['GET'])
def getSolarData():
    """
    Returns the solar data in dictionary format
    """
    rd = get_redis_client(0)
    solarData = {}
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    for panelType in rd.keys():
        solarData[panelType] = rd.hgetall(panelType)
    return solarData

@app.route('/solar/categories', methods=['GET'])
def getSolarCategories():
    """
    Returns the available categories in the solar data
    """
    rd = get_redis_client(0)
    solarCategories = []
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    panelType = list(rd.keys())[0]
    solarCategories = list(rd.hgetall(panelType).keys())
    return solarCategories

@app.route('/solar/categories/<category>', methods=['GET'])
def getSolarCategoryData(category: str) -> List[str]:
    """
    Returns the data for the given category in the solar data

    Args:
        category: string that contains the category name

    Returns:
        solarCategories: dictionary containing the solar data of the given category
    """
    rd = get_redis_client(0)
    solarCategories = {}
    if not checkData():
        return "Error: Data not found. Please load the data.\n", 400
    if not checkSolarCategories(category):
        return "Error: Category not found. Available categories can be found at /solar/categories.\n", 400
    for panelType in rd.keys():
        solarCategories[panelType] = rd.hget(panelType, category)
    return solarCategories

def checkSolarCategories(category: str):
    """
    Checks if the category exists in the solar data

    Returns:
        True: if the category exists
        False: otherwise
    """
    rd = get_redis_client(0)
    panelType = list(rd.keys())[0]
    solarCategories = rd.hgetall(panelType).keys()
    return category in solarCategories

@app.route('/jobs', methods=['POST'])
def postJobs():
    """
    API route for creating a new job to do some analysis. This route accepts a JSON payload
    describing the job to be created.
    """
    try:
        job = request.get_json(force=True)
    except Exception as e:
        return json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    if isinstance(job['param'], dict):
        return jobs.add_job(job['type'], json.dumps(job['param']))
    return jobs.add_job(job['type'], job['param'])

@app.route('/jobs', methods=['GET'])
def getJobs():
    """
    API route for getting a list of current jobs.
    """
    rd = get_redis_client(7)
    return list(rd.keys())

@app.route('/jobs/<id>', methods=['GET'])
def getJob(id):
    """
    API route for getting a job given a job id.
    """
    rd = get_redis_client(7)
    if id not in rd.keys():
        return "Error: Job id not found. Available job ids can be found at /jobs.\n", 400
    return dict(zip(['start','end','status','type','param'],rd.hmget(id,'start','end','status','type','param')))

@app.route('/jobs/<id>/results', methods=['GET'])
def getJobResults(id):
    """
    API route for getting job results given a job id.
    """
    rd = get_redis_client(7)
    if id not in rd.keys():
        return "Error: Job id not found. Available job ids can be found at /jobs.\n", 400
    rd = get_redis_client(7, False)
    return rd.hget(id, 'results')

@app.route('/help', methods=['GET'])
def get_help():
    """ 
        get_help function that returns a help text for the user giving brief descriptions of all available routes (plus their methods) of the API
        Args: 
            No Args 
        Return: 
            help_string - a string containing the help text for each route
    """
    help_string = "Usage: curl jakew57.coe332.tacc.cloud/route\n\n"
    help_string += "Available routes:\n\n"
    help_string += "   /data - Gets the weather data and returns the data in dictionary format.  \n"
    help_string += "   /cities  - Gets the weather data and returns the list of cities.\n"
    help_string += "   /weather/cities  -  Returns a dateList a list of cities (strings) for which\n" 
    help_string += "                       weather data is available.\n"
    help_string += "   /weather/cities/<city>   -   Gets the weather data and returns the data for a given city.\n\n"
    help_string += "   /weather/cities/<city>/dates   -   Gets the weather data and returns the list of dates in a list.\n"
    help_string += "   /weather/cities/<city>/dates/<date>  - Gets the weather data, then returns the weather\n"
    help_string += "            data for a given date/city, if available.\n"
    help_string += "   /help  - Returns an string giving helpful information.\n"
    help_string += "   /weather/categories  - Gets the weather data, then returns the categories for \n"
    help_string += "            weather data of a given date/city, if available.\n"
    help_string += "   /weather/cities/<city>/categories/<category> - Gets the weather data, then returns the\n" 
    help_string += "            weather data of a given category for a given city, if available.\n"
    help_string += "   /solar  -  Gets the solar data from the data base.\n"
    help_string += "   /solar/categories  -   Gets the list od categories in the solar data base.\n"
    help_string += "   /solar/categories/<category>   - Gets the specific category of a given category in the solar\n"
    help_string += "                                    database.\n"
    help_string += "   /jobs  - Returns the list of jobs in the database.\n"
    help_string += "   /jobs/<id>  - Returns info about a given job.\n"
    help_string += "   /jobs/<id>/results  - Returns the results of a given job.\n"
    help_string += "Usage: curl -X POST jakew57.coe332.tacc.cloud/route\n\n"
    help_string += "   /data  - Gets the weather/solar panel data and saves the data in dictionary \n"
    help_string += "            format in the flask app. Returns a String.\n"
    help_string += "   /jobs -d @<filename> - Post a job into the database using a json file.\n"
    help_string += "Usage: curl -X DELETE jakew57.coe332.tacc.cloud/route\n"
    help_string += "   /data  - Deletes the data stored in the redis db returns a success message.\n"
    return help_string

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
