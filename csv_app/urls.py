# -*- coding: utf-8 -*-
from django.conf.urls import url
from csv_app.views import list, detail, object_delete, viewLogs

app_name = 'csv_app'

urlpatterns = [
    #/documents
    url(r'^$', list, name='list'),
    #/documents/<doc_slug>
    url(r'^(?P<document_slug>[-\w\d]+)$', detail, name='detail'),
    #/documents/delete/<doc_id>
    url(r'^delete/(?P<document_id>[0-9]+)$', object_delete, name='delete'),
    #/documents/<doc_slug>/logs
    url(r'^(?P<document_slug>[-\w\d]+)/logs$', viewLogs, name='logs'),
]
