# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from csv_app.forms import DocumentForm
from django.template import loader
import csv
import codecs
from csv_app.models import *
def index(request):
    all_documents = Document.objects.all()
    template = loader.get_template('documents/index.html')
    context = {
        'all_documents':all_documents,
    }
    #return HttpResponse(template.render(context, request))
    return render(request, 'documents/index.html', context)


#If an object from the list is pressed
def detail(request, document_slug):
    try:
        document = Document.objects.get(slug = document_slug)
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    return render(request, 'documents/detail.html', {'document': document})
# https://www.youtube.com/watch?v=mWofrhTwGWQ&list=PL6gx4Cwl9DGBlmzzFcLgDhKTTfNLfX1IK&index=12


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

                # Adding the CSV into the DB
                if not db_table_exists(newdoc.title):
                    #If it does not exist, we create a
                    with open("./media/"+newdoc.docfile.name, "r") as csvfile:
                        csv_reader = csv.reader(csvfile)
                        header_list = []
                        header_list.append(csv_reader)
                        print("reached")
                        attrs = {title:models.CharField(max_length=35) for title in header_list}
                        new_model = type(newdoc.title, (models.Model,),attrs)
                        new_model.save()


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

def db_table_exists(table, cursor=None):
    try:
        if not cursor:
            from django.db import connection
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        table_names = connection.introspection.get_table_list(cursor)
    except:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in table_names