from flask import Flask, request, send_file

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
