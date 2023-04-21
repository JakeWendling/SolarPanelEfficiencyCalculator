import uuid
from hotqueue import HotQueue
from redis import Redis
import os

# create the q and rd objects using the variable
redis_ip = os.environ.get('REDIS_IP')
q = HotQueue("queue", host=redis_ip, port=6379, db=8)

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
    rd = redis.Redis(host=redis_ip, port=6379, db=db, decode_responses=decode)
    return rd

def generate_jid():
    """      
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())

def instantiate_job(jid, jtype, param, status, start, end):
    """
    Create the job object description as a python dictionary. Requires the job id, status,
    start and end parameters.
    """
    if type(jid) == str:
        return {'id': jid,
                'type': jtype,
                'param': param,
                'status': status,
                'start': start,
                'end': end
        }
    return {'id': jid.decode('utf-8'),
            'type': jtype.decode('utf-8'),
            'param': param.decode('utf-8'),
            'status': status.decode('utf-8'),
            'start': start.decode('utf-8'),
            'end': end.decode('utf-8')
    }

def generate_job_key(jid):
    """
    Generate the redis key from the job id to be used when storing, retrieving or updating
    a job in the database.
    """
    return 'job.{}'.format(jid)

def _save_job(job_key, job_dict):
    """Save a job object in the Redis database."""
    rd = get_redis_client(7, False)
    rd.hset(job_key, mapping=job_dict)

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)

def add_job(jtype, param, start, end, status="submitted"):
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, jtype, param, status, start, end)
    # update call to save_job:
    save_job(_generate_job_key(jid), job_dict)
    # update call to queue_job:
    queue_job(jid)
    return job_dict
    
def update_job_status(jid, status):
    """Update the status of job with job id `jid` to status `status`."""
    job = get_job_by_id(jid)
    if job:
        job['status'] = status
        _save_job(_generate_job_key(jid), job)
    else:
        raise Exception()
