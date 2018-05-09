# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from csv_app.forms import DocumentForm
from django.template import loader
import csv
import codecs
from csv_app.models import *
from csv_app.utils import importCSV_inDB, exportCSV_fromDB, deleteCSV_fromDB, exportLog_fromDB
from django.contrib.auth import get_user
import os
import shutil
from django.core.files import File

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
        existing_doc = Document.objects.get(slug = document_slug)
        csv_content, header_list = exportCSV_fromDB('./media/' + existing_doc.docfile.name, './mydatabase')
    except Document.DoesNotExist:
        raise Http404("Document does not exist")

    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = Document(docfile=request.FILES['docfile'])
        if newdoc.docfile.name != existing_doc.docfile.name:
            newdoc.docfile.name = existing_doc.docfile.name
            newdoc.title = existing_doc.title

        # Checks if uploaded doc is CSV
        if Document(docfile=request.FILES['docfile']).docfile.name.split('.')[1] == 'csv':
            # Check if log dir exists, else create
            raw_doc = Document(docfile=request.FILES['docfile'])
            if not os.path.exists('./media/logs/'+existing_doc.title):
                os.makedirs('./media/logs/'+existing_doc.title)
            if not os.path.exists('./media/backups/'+existing_doc.title):
                os.makedirs('./media/backups/'+existing_doc.title)

            # Move old file to the log directory
            shutil.move('./media/' + existing_doc.docfile.name, './media/backups/'+existing_doc.title)

            # Rename old file
            info_file_name = (existing_doc.title + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[
                0] + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[1] + '.csv').replace(":", "-")

            backup_path_name ='./media/backups/' + existing_doc.title + '/' + info_file_name

            os.rename('./media/backups/'+existing_doc.title+'/' + existing_doc.docfile.name, backup_path_name)

            logged_file_document = open(backup_path_name)
            django_file = File(logged_file_document)

            # Set up and save new document
            newdoc.title = newdoc.docfile.name.replace(".csv", "")
            newdoc.slug = newdoc.title.replace(" ", "-")
            newdoc.save()

            # Create Log
            new_log = Log(user=get_user(request).get_username(), datetime=((str(datetime.datetime.now())).split('.')[0]).split(' ')[
                        0] + ' ' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[1],
                      document= existing_doc.docfile, filename=raw_doc.docfile.name, action='Edit', slug=document_slug)
            new_log.document.save('./logs/' + existing_doc.title + '/' + info_file_name, django_file)
            new_log.save()
            print('log file name: ', new_log.document.name)
            print('existing_doc.docfile.name', existing_doc.docfile.name)

            Document.objects.filter(id=existing_doc.id).delete()

            print('POST FILTER existing_doc.docfile.name', existing_doc.docfile.name)
            existing_doc = Document.objects.get(slug=document_slug)
            deleteCSV_fromDB('./media/' + existing_doc.docfile.name, './mydatabase')
            importCSV_inDB('./media/' + newdoc.docfile.name, './mydatabase')
    all_logs = Log.objects.filter(slug=document_slug)
    return render(request, 'documents/detail.html', {'document': existing_doc,
                                                         'csv_content': csv_content, 'header_list': header_list,
                                                         'form': form, 'all_logs':all_logs})

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
                old_doc = Document(docfile=request.FILES['docfile'])

                newdoc = Document(docfile=request.FILES['docfile'])
                newdoc.title = newdoc.docfile.name.split('.')[0]

                #Generate the Url per object (slug)
                if ' ' in newdoc.title:
                    newdoc.slug = newdoc.title.replace(' ', '-')
                else:
                    newdoc.slug = newdoc.title
                newdoc.save()

                importCSV_inDB('./media/' + newdoc.docfile.name, './mydatabase')
                newdoc.docfile.name = newdoc.title + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[0] + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[1] + '.csv'
                new_log = Log(user=get_user(request).get_username(), datetime=datetime.datetime.now(), document=newdoc.docfile, filename=old_doc.title, action='Upload', slug=newdoc.slug)
                new_log.save()
                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('csv_app:list'))

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


def object_delete(request, document_id):

    if request.method == 'POST':
        document = get_object_or_404(Document, pk=document_id)
        try:
            os.remove('./media/' + document.docfile.name)
        except OSError:
            pass

        deleteCSV_fromDB('./media/' + document.docfile.name, './mydatabase')
        document.delete()
    return redirect('csv_app:list')


def viewLogs(request, document_slug):

    if request.method == 'POST':
        print('doc slug:' + document_slug)

        headers = ['User', 'DateTime', 'FileName', 'Action' ]
        content = exportLog_fromDB(document_slug,  './mydatabase')
        print(content)
    return render(
        request,
        'documents/logs.html',
        {'headers': headers, 'content': content}
    )