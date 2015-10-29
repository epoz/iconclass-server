from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import urllib
import iconclass
import json
import elasticsearch
import redis

def home(request):
    context = {'root' : iconclass.get_list('0 1 2 3 4 5 6 7 8 9'.split(' '))}
    return render(request, 'home.html', context)

@csrf_exempt
def githubwebhook(request):
    data = request.read()
    redis_c = redis.StrictRedis()
    redis_c.lpush(settings.REDIS_PREFIX + '_gitpushes', data)
    return HttpResponse("OK")


def search(request):
    q = request.GET.get('q')
    context = {'q':q}
    if q:
        es = elasticsearch.Elasticsearch()
        results = es.search(index=settings.ES_INDEX_NAME+'_en', 
                            q=q, fields=['notation'],
                            default_operator='AND', size=99)
        context['count'] = results['hits']['total']
        notations = [r['fields']['notation'][0] for r in results['hits']['hits']]
        context['notation_objs'] = iconclass.get_list(notations)
    return render(request, 'search.html', context)


def browse(request, language, notation='0'):
    if language == 'rkd':
        return HttpResponseRedirect('/en/'+notation+'/')
    path_objs = iconclass.get_list(iconclass.get_parts(notation))
    notation_obj = path_objs[-1]
    if 'c' in notation_obj:
        children_objs  = iconclass.get_list(notation_obj['c'])
    else:
        children_objs = []
    context = {
        'root' : iconclass.get_list('0 1 2 3 4 5 6 7 8 9'.split(' ')),
        'notation_obj' : path_objs[0],
        'path_objs' : path_objs,
        'children_objs' : children_objs,
        'language' : language
    }
    return render(request, 'browse.html', context)


def sw(request, notation):
    'Semantic Web - Linked Data'
    if notation.endswith('.rdf'):
        return linked_data(request, 'rdf', notation[:-4])
    if notation.endswith('.json'):
        return linked_data(request, 'json', notation[:-5])
    if notation.endswith('.fat'):
        return linked_data(request, 'fat', notation[:-4])
    if request.META.get('HTTP_ACCEPT').find('application/rdf+xml') > -1:
        response = HttpResponseRedirect('/' + urllib.quote(notation) +'.rdf')
        response.status_code = 303
        return response
    return HttpResponseRedirect('/en/'+notation+'/')


def linked_data_list(request, format):
    notations = request.REQUEST.getlist('notation')
    data = iconclass.get_list(notations)
    if format == 'rdf':
        tmp = loader.render_to_string('rdf.html', {'obj_list':data})
        return HttpResponse(tmp, content_type='application/xml')
    if format == 'fat':
        for obj in data:
            iconclass.fill_obj(obj)
            if 'comments' in obj:
                del obj['comments']

    return HttpResponse(json.dumps(data, indent=2), content_type='application/json')


def linked_data(request, format, notation):
    if notation == 'scheme':
        SKOSRDF = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <skos:ConceptScheme rdf:about="http://iconclass.org/rdf/2011/09/">
        <dc:title>ICONCLASS</dc:title>
        <dc:description>Iconclass is a subject-specific multilingual classification system. It is a hierarchically ordered collection of definitions of objects, people, events and abstract ideas that serve as the subject of an image. Art historians, researchers and curators use it to describe, classify and examine the subject of images represented in various media such as paintings, drawings, photographs and texts.</dc:description>
        <dc:creator>Henri van de Waal</dc:creator>
        <skos:hasTopConcept rdf:resource="http://iconclass.org/ICONCLASS"/>
   </skos:ConceptScheme>
</rdf:RDF>'''
        return HttpResponse(SKOSRDF, content_type='application/xml')
    if notation == 'ICONCLASS':
        obj = {'txt':{'en':'ICONCLASS Top'}, 'c':[str(x) for x in range(10)]}
    else:
        obj = iconclass.get(notation)
    if format == 'rdf':
        tmp = loader.render_to_string('rdf.html', {'obj_list':[obj]})
        return HttpResponse(tmp, content_type='application/xml')
    if format == 'fat':
        obj = iconclass.fill_obj(obj)
        if 'comments' in obj:
            del obj['comments']
    return HttpResponse(json.dumps(obj, indent=2), content_type='application/json')
