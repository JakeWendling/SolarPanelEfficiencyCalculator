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
    cities = ['Dallas', 'Austin', 'Houston', 'San_Antonio']
    for i in range(len(cities)):
        city = cities[i]
        with open(f'data/{city}.json', 'r') as f:
            rd = get_redis_client(i+1)
            data = json.load(f)
            for day in data['days']:
                day.pop('stations')
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
    Gets the HGNC data and returns the data in dictionary format

    Returns:
        data: The stored data in dictionary format.
    """
    rd = get_redis_client()
    data = []
    for key in rd.hgetall('data'):
        data.append(json.loads(rd.hget('data', key)))
    #if data == "":
    #    return "Data not found\n", 400
    return data

@app.route('/genes', methods=['GET'])
def getGenes() -> List[str]:
    """
    Gets the HGNC data and returns the list of genes in a list
    
    Returns:
        idList: a list of id's of genes(strings) for which gene data is available.
    """
    #if not data:
    #    return "Data not found\n", 400
    #geneList = data['response']['docs']
    rd = get_redis_client()
    return rd.hkeys('data')

@app.route('/genes/<hgnc_id>', methods=['GET'])
def getGene(hgnc_id: str) -> dict:
    """
    Gets the HGNC data, 
    then returns the gene data for a given HGNC ID, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        hgnc_id: A string representing a gene's HGNC ID.
        
    Returns:
        geneData: Dictionary containing data about the given gene, if available. 
    
    Raises:
        If no gene data is available for the given gene id, 
        returns an error message and a 400 status code.
    """
    rd = get_redis_client()
    for key in rd.hkeys('data'):
        gene = json.loads(rd.hget('data', key))
        if gene['hgnc_id'] == hgnc_id:
            return gene
    return "Error: Gene not found\n", 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    rd = get_redis_client()
    if rd.keys() == []:
        postData()
    
