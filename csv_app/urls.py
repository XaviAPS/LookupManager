# -*- coding: utf-8 -*-
from django.conf.urls import url
from csv_app.views import list, detail, objectDelete


urlpatterns = [
    #/documents
    url(r'^$', list, name='list'),
    #/documents/<doc_slug>
    url(r'^(?P<document_slug>[-\w\d]+)$', detail, name='detail'),
    #/documents/<doc_slug>/delete
    url(r'^(?P<document_slug>[-\w\d]+/delete)$', objectDelete, name='delete'),
]
