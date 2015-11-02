import elasticsearch, elasticsearch.helpers
import iconclass
from django.conf import settings
import redis

def go():
    es = elasticsearch.Elasticsearch()
    esi = elasticsearch.client.IndicesClient(es)
    esi.delete(index=settings.ES_INDEX_NAME + '_en')
    init_index('en')
    print index('12A1', 'en')
    r = es.search(index=settings.ES_INDEX_NAME + '_en', fields=['notation'])
    print r['hits']['total']
    for h in r['hits']['hits']:
        print h['fields'].get('notation')[0]


def init_index(language):
    ES_MAPPINGS = {

    "en" : { "notation" : {
        "_source": {"enabled":  False },
        "properties" : {
            "notation": {"type": "string", "store": True, "index": "not_analyzed" },
            "txt": {"type": "string", "store": False, "analyzer": "english"}
        }
      }
    }

    }

    if language not in ES_MAPPINGS:
        raise Exception('Language %s not found in ES_MAPPINGS %s' % (language, ES_MAPPINGS.keys()))
    esi = elasticsearch.client.IndicesClient(elasticsearch.Elasticsearch())
    esi.create(index=settings.ES_INDEX_NAME + '_' + language, body={"mappings":ES_MAPPINGS.get(language)})


def ixable(obj, language):
    path_texts = [p.get('txt', {}).get(language, u'') for p in iconclass.get_list(obj.get('p', [])) if p]
    o = {}
    o['_index'] = settings.ES_INDEX_NAME + '_' + language
    o['_type'] = 'notation'
    o['_id'] = hash(obj['n'])
    o['_source'] = {
        'txt': '\n'.join(path_texts),
        'notation': obj['n']
    }
    return o


def ixable_iterator(notation, language, skip_keys=True):
    obj = iconclass.get(notation)
    if not obj: return
    yield ixable(obj, language)
    for k in obj.get('c', []):
        if skip_keys and k.find('(+') > 0: continue
        for kk in ixable_iterator(k, language):
            yield kk


def fill_redis_q(notation, language):
    redis_c = redis.StrictRedis()
    count = 0
    for x in index_iterator(notation, language):
        q_size = redis_c.lpush(settings.REDIS_PREFIX + '_ic_index_q', x)
        count += 1
    return q_size, count


def index_iterator():
    redis_c = redis.StrictRedis()
    while True:
        tmp = redis_c.lpop(settings.REDIS_PREFIX + '_ic_index_q')
        if not tmp: break
        yield tmp

def index(language):
    success_count, errors = elasticsearch.helpers.bulk(elasticsearch.Elasticsearch(), 
                                                       index_iterator(),
                                                       chunk_size=9999)
    return success_count, errors