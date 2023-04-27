import uuid
from hotqueue import HotQueue
from redis import Redis
from datetime import datetime
import os

# create the q and rd objects using the variable
redis_ip = os.environ.get('REDIS_IP')

def get_hotqueue():
    """
    Returns the hotqueue object
    """
    q = HotQueue("queue", host=redis_ip, port=6379, db=8)
    return q

q = get_hotqueue()

def get_redis_client(db: int=0, decode: bool=True):
    """
    Gives the redis db object

    Args:
        db: (int) database index/page
        decode: (bool) whether to decode byte responses to str

    Returns:
        rd: redis object
    """
    global redis_ip
    #redis_ip = os.environ.get('REDIS_IP')
    if not redis_ip:
        raise Exception('Error: Ip not found')
    rd = Redis(host=redis_ip, port=6379, db=db, decode_responses=decode)
    return rd

def _get_job_by_id(jid: str) -> dict:
    """
    Returns the job of the given id
    """
    rd = get_redis_client(7, False)
    job = rd.hgetall(_generate_job_key(jid))
    return job
    
def _generate_jid() -> str:
    """      
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())

def _instantiate_job(jid: str, jtype: str, param: str, status: str) -> dict:
    """
    Create the job object description as a python dictionary. Requires the id, status, type 
    and parameter for the job.
    """
    start = str(datetime.now())
    if type(jid) == str:
        return {'id': jid,
                'type': jtype,
                'param': param,
                'status': status,
                'start': start,
        }
    return {'id': jid.decode('utf-8'),
            'type': jtype.decode('utf-8'),
            'param': param.decode('utf-8'),
            'status': status.decode('utf-8'),
            'start': start,
    }

def _generate_job_key(jid: str) -> str:
    """
    Generate the redis key from the job id to be used when storing, retrieving or updating
    a job in the database.
    """
    return 'job.{}'.format(jid)

def _save_job(job_key: str, job_dict: dict):
    """Save a job object in the Redis database."""
    rd = get_redis_client(7, False)
    rd.hset(job_key, mapping=job_dict)

def _queue_job(jid: str):
    """Add a job to the redis queue."""
    q.put(jid)

def add_job(jtype: str, param: str, status:str="submitted") -> dict:
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, jtype, param, status)
    # update call to save_job:
    _save_job(_generate_job_key(jid), job_dict)
    # update call to queue_job:
    _queue_job(jid)
    return job_dict
    
def update_job_status(jid: str, status: str):
    """Update the status of job with job id `jid` to status `status`."""
    job = _get_job_by_id(jid)
    if job:
        job['status'] = status
        _save_job(_generate_job_key(jid), job)
    else:
        raise Exception()

def update_job_end(jid: str):
    """
    Update the end time of the job with the current time.
    """
    job = _get_job_by_id(jid)
    currentTime = str(datetime.now())
    if job:
        job['end'] = currentTime
        _save_job(_generate_job_key(jid), job)
    else:
        raise Exception()

def update_job_results(jid: str, results: dict):
    """
    Update the end time of the job with the current time.
    """
    job = _get_job_by_id(jid)
    if job:
        job[b'results'] = results
        _save_job(_generate_job_key(jid), job)
    else:
        raise Exception()

def get_job_type(jid: str) -> str:
    job = _get_job_by_id(jid)
    if job:
        return job[b'type'].decode('utf-8')
    else:
        raise Exception()

def get_job_param(jid: str) -> str:
    job = _get_job_by_id(jid)
    if job:
        return job[b'param'].decode('utf-8')
    else:
        raise Exception()
