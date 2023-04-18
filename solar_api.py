import requests
import redis
import json
from typing import List
from flask import Flask, request, send_file
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

def get_redis_client(db=0, decode=True):
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
    cities = {'Dallas': 1, 'Austin': 2, 'Houston': 3, 'San_Antonio': 4}
    return cities
    
@app.route('/image', methods=['DELETE'])
def deleteImage() -> dict:
    """
    Deletes the image stored in the redis db

    Returns:
        string: success message
    """
    rd = get_redis_client(1, False)
    if rd.keys() == []:
        return 'Error, no image exists in the database\n', 400
    rd.delete('image')
    return 'Image deleted from database\n'

@app.route('/image', methods=['GET'])
def getImage() -> bytes:
    """
    Gets the image stored in the redis db

    Returns:
        image: plot image as bytes
    """
    rd = get_redis_client(1, False)
    if rd.keys() == []:
        raise Exception('Error: no image exists in the database')
    image = rd.get('image')
    return image
    #return send_file(image, mimetype='image/png', as_attachment=True, download_name='plot.png')

@app.route('/image', methods=['POST'])
def postImage() -> tuple:
    """
    Creates a plot of the locus groups of the gene data and stores the image in redis 

    Returns:
        string: success message
    """
    redis_genes = get_redis_client(0)
    redis_image = get_redis_client(1, False)

    if redis_genes.hkeys('data') == []:
        return 'Error, data has not been loaded into the database\n', 400
    
    graph_data = {}
    for gene in redis_genes.hkeys('data'):
        gene_data = json.loads(redis_genes.hget('data', gene))
        locus_group = gene_data['locus_group']
        if locus_group in graph_data:
            graph_data[locus_group] += 1
        else:
            graph_data[locus_group] = 1
    
    plt.bar(graph_data.keys(),graph_data.values())
    plt.ylabel('Count')
    plt.title('Counts of Locus Groups in HGNC Gene Data')
    plt.xticks(rotation = 15)
    plt.savefig('plot.png')
    file_bytes = open('plot.png', 'rb').read()
    redis_image.set('image', file_bytes)
    
    return 'Image saved to database\n'

@app.route('/data', methods=['POST'])
def postData() -> dict:
    """
    Gets the weather/solar panel data and saves the data in dictionary format in the flask app.

    Returns:
        string: Message that tells the user that the data has successfuly been obtained
    """
    #response = requests.get('https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json')
    cities = getCities()
    for i in range(len(cities)):
        city = cities[i]
        with open(f'data/{city}.json', 'r') as f:
            rd = get_redis_client(i+1)
            data = json.load(f)
            for day in data['days']:
                day.pop('stations')
                if day['preciptype']:
                    day['preciptype'] = ', '.join(day['preciptype'])
                else:
                    day['preciptype'] = 'none'
                print(day)
                rd.hset(day['datetime'], mapping=day)
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
    Gets the weather data and returns the data in dictionary format

    Returns:
        data: The stored data in dictionary format.
    """
    data = []
    cities = getCities()
    for city in cities.keys():
        rd = get_redis_client(cities[city])
        for date in rd.hkeys():
            data.append(rd.hgetall(date))
    #if data == "":
    #    return "Data not found\n", 400
    return data

@app.route('weather/<city>/date', methods=['GET'])
def getDates(city: str) -> List[str]:
    """
    Gets the weather data and returns the list of dates in a list
    
    Returns:
        dateList: a list of dates (strings) for which weather data is available.
    """
    #if not data:
    #    return "Data not found\n", 400
    cities = getCities()
    rd = get_redis_client(city)
    return rd.keys()

@app.route('weather/cities', methods=['GET'])
def getCities() -> List[str]:
    """
    Gets the weather data and returns the list of cities
    
    Returns:
        dateList: a list of cities (strings) for which weather data is available.
    """
    #if not data:
    #    return "Data not found\n", 400
    cities = getCities()
    return cities.keys()

@app.route('weather/<city>/date/<date>', methods=['GET'])
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
    cities = getCities()
    rd = get_redis_client(cities[city])
    try:
        weatherData = rd.hgetall(date)
    except Exception as e:
        #return "Error: Data not found, please enter a different date. Available dates can be found in weather/dates \n", 400
        return e
    return weatherData

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    rd = get_redis_client()
    if rd.keys() == []:
        postData()
    
