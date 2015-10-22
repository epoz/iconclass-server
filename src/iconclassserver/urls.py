from django.conf.urls import include, url
from django.contrib import admin

import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.home, name='home'),
    url(r'^(.+)/([\w|0-9|\'\:\.\,\-\& \+\(\)\.]+)/$', views.browse, name='browse'),
    url(r'^search$', views.search, name='search'),
    url(r'^githubwebhook$', views.githubwebhook, name='githubwebhook'),

    url(r'^rdf/2011/09/$', views.linked_data, {'format':'rdf', 'notation':'scheme'}),
    url(r'^ICONCLASS$', views.linked_data, {'format':'rdf', 'notation':'ICONCLASS'}),    
    url(r'^([\w|0-9|\'\:\.\,\-\& \+\(\)\.]+)$', views.sw),
    url(r'^(_|json|rdf|fat)/([\w|0-9|\'\:\.\,\-\& \+\(\)\.]+)$', views.linked_data),
    url(r'^(json|rdf|fat)/', views.linked_data_list),
]
