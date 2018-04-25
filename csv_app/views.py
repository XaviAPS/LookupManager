# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from csv_app.forms import DocumentForm
from django.template import loader
import csv
import codecs
from csv_app.models import *
from csv_app.utils import importCSV_inDB, exportCSV_fromDB, deleteCSV_fromDB

def index(request):
    all_documents = Document.objects.all()
    template = loader.get_template('documents/index.html')
    context = {
        'all_documents':all_documents,
    }
    return render(request, 'documents/index.html', context)


#If an object from the list is pressed
def detail(request, document_slug):
    try:
        document = Document.objects.get(slug = document_slug)
        csv_content, header_list = exportCSV_fromDB('./media/' + document.docfile.name, './mydatabase')
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    return render(request, 'documents/detail.html', {'document': document,
                                                     'csv_content': csv_content, 'header_list': header_list})



def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        all_docs = Document.objects.all()
        repeated = False
        is_csv = False
        if form.is_valid():

            #Checks if the name of the file is already in the DB
            for doc in all_docs:
                if Document(docfile=request.FILES['docfile']).docfile.name.split('.')[0] == doc.docfile.name.split('.')[0]:
                    repeated = True

            #Checks if uploaded doc is CSV
            if Document(docfile=request.FILES['docfile']).docfile.name.split('.')[1] == 'csv':
                is_csv = True

            #Stores it in DB and in /media
            if not repeated and is_csv:
                newdoc = Document(docfile=request.FILES['docfile'])
                newdoc.title = newdoc.docfile.name.split('.')[0]

                #Generate the Url per object (slug)
                if ' ' in newdoc.title:
                    newdoc.slug = newdoc.title.replace(' ', '-')
                else:
                    newdoc.slug = newdoc.title
                newdoc.save()

                importCSV_inDB('./media/' + newdoc.docfile.name, './mydatabase')

                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('list'))

    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'documents/list.html',
        {'documents': documents, 'form': form}
    )

def show_view(request):
    if request.POST and request.FILES:
        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        reader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=',', dialect=dialect)

    return render(request, "documents/csv_read.html", locals())

def objectDelete(request, object_slug):

    object = get_object_or_404(Document, pk=object_slug)
    try:
        os.remove('./media/' + object.docfile.name + '.csv')
    except OSError:
        pass

    deleteCSV_fromDB('./media/' + object.docfile.name, './mydatabase')
    object.delete()