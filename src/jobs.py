import uuid
from hotqueue import HotQueue
from redis import Redis

q = HotQueue("queue", host='172.17.0.1', port=6379, db=1)
rd = redis.Redis(host='172.17.0.1', port=6379, db=0)


def generate_jid():
      """
      Generate a pseudo-random identifier for a job.
      """
      return str(uuid.uuid4())

def instantiate_job(jid, status, start, end):
      """
      Create the job object description as a python dictionary. Requires the job id, status,
      start and end parameters.
      """
      if type(jid) == str:
          return {'id': jid,
                  'status': status,
                  'start': start,
                  'end': end
          }
      return {'id': jid.decode('utf-8'),
              'status': status.decode('utf-8'),
              'start': start.decode('utf-8'),
              'end': end.decode('utf-8')
      }


def _save_job(job_key, job_dict):
    """Save a job object in the Redis database."""
    rd.hset(job_key, mapping=job_dict)

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)


def add_job(start, end, status="submitted"):
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, start, end)
    # update call to save_job:
    save_job(_generate_job_key(jid), job_dict)
    # update call to queue_job:
    queue_job(jid)
    return job_dict

def efficiencyCalculator():

    efficiency_list = []
    efficiency_list.append(total)


    #for loops for each solar pane
    rd_solar = get_redis_client(0)
    for panelType in rd_solar.hkeys():
        
        

        rd = get_redis_client(cities[city])
        total = 0
        for date in rd.keys():
        
            efficiency = rd_solar.hget(panelType, "Efficiency")
            weatherData = rd.hgetall(date)
            temperature = weatherData["temp"]
            sunsetEpoch = weatherData["sunsetEpoch"]
            sunriseEpoch = weatherData["sunriseEpoch"]
            cloudcover = weatherData["cloudcover"]

            total += (temperature - 25) * efficiency * cloud cover * (sunsestepoch - sunriseepoch)

        efficiency_list.append(total)
    return list(rd_solar.hkeys())[efficiency_list.index(max(list))]
    
