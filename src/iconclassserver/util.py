import redis
import json
from django.conf import settings
import iconclass
import requests
import time
import os

def handle_githubpushes():
    redis_c = redis.StrictRedis()
    while True:
        data = redis_c.lpop(settings.REDIS_PREFIX + '_gitpushes')
        if not data: break
        data = json.loads(data)        
        full_name = data['repository']['full_name']
        for commit in data.get('commits', []):
            committer = commit['committer']['email']
            timestamp = commit['timestamp']
            commit_id = commit['id']
            for filename in commit['modified']:
                if filename.startswith('data/'):
                    head, tail = os.path.split(filename)
                    fn, language = iconclass.action(tail)
                    if not fn: continue
                    r = requests.get('https://raw.githubusercontent.com/'+full_name+'/master/'+filename)
                    if r.status_code == 200:
                        fn(r.content, language)
                        buf = [time.strftime('%Y%m%d %H:%M:%S'), committer, filename, timestamp, commit_id]
                        redis_c.lpush(settings.REDIS_PREFIX + '_gitpushlog', ' '.join(buf))