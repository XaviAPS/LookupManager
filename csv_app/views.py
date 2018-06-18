# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from csv_app.forms import DocumentForm
from csv_app.models import *
from csv_app.utils import *
from django.contrib.auth import *
import os
import shutil
from django.core.files import File
from django.contrib.auth.urls import *
from django.contrib.auth.decorators import login_required

#If an object from the list is pressed


@login_required(login_url='/account/login/')
def detail(request, document_slug):
    try:
        existing_doc = Document.objects.get(slug = document_slug)
        csv_content, header_list = exportCSV_fromDB('./media/' + existing_doc.docfile.name, './mydatabase')

    except Document.DoesNotExist:
        raise Http404("Document does not exist")

    csv_to_JSON('./media/' + existing_doc.docfile.name, './media/tmp/tmp.json')
    form = DocumentForm(request.POST, request.FILES)
    print('URL: ', existing_doc.docfile.url)
    print('newurl: ',existing_doc.json_url)

    if request.GET.get("download_JSON"):
        print("asdasdasd")
        print(type(existing_doc.docfile.url))

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
            existing_doc = Document.objects.get(slug=document_slug)
            deleteCSV_fromDB('./media/' + existing_doc.docfile.name, './mydatabase')
            importCSV_inDB('./media/' + newdoc.docfile.name, './mydatabase')
    return render(request, 'documents/detail.html', {'document': existing_doc,
                                                         'csv_content': csv_content, 'header_list': header_list,
                                                         'form': form})

@login_required(login_url='/account/login/')
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

                old_doc.title = newdoc.title

                if not os.path.exists('./media/logs/' + old_doc.title):
                    os.makedirs('./media/logs/' + old_doc.title)
                if not os.path.exists('./media/backups/' + old_doc.title):
                    os.makedirs('./media/backups/' + old_doc.title)


                #Generate the Url per object (slug)

                newdoc.slug = newdoc.title.replace(' ', '-')
                newdoc.save()


                importCSV_inDB('./media/' + newdoc.docfile.name, './mydatabase')


                #Name variables of paths
                info_file_name = (newdoc.title + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[
                    0] + '_' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[1] + '.csv').replace(":", "-")

                # Move old file to the log directory
                shutil.copy2('./media/' + old_doc.docfile.name, './media/backups/' + newdoc.title)

                backup_path_name = './media/backups/' + newdoc.title + '/' + info_file_name

                os.rename('./media/backups/' + newdoc.title + '/' + old_doc.docfile.name, backup_path_name)

                logged_file_document = open(backup_path_name)
                django_file = File(logged_file_document)

                #Log Creation
                new_log = Log(user=get_user(request).get_username(), datetime=((str(datetime.datetime.now())).split('.')[0]).split(' ')[
                                           0] + ' ' + ((str(datetime.datetime.now())).split('.')[0]).split(' ')[1], document=old_doc.docfile.name, filename=old_doc.docfile.name, action='Upload', slug=newdoc.slug)
                new_log.document.save('./logs/' + newdoc.title + '/' + info_file_name, django_file)
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

@login_required(login_url='/account/login/')
def viewLogs(request, document_slug):

    # if request.method == 'POST':
    print('doc slug:' + document_slug)

    headers = ['User', 'DateTime', 'FileName', 'Action',]
    content = exportLog_fromDB(document_slug,  './mydatabase')
    form = DocumentForm(request.POST, request.FILES)


    lines = []
    for j, line in enumerate(content):
        lines.append(tuple(line))
        #lines.append(logged_docs[j])


    all_logs = Log.objects.filter(slug=document_slug)
    logged_docs = []
    for x, log in enumerate(all_logs):
        lines[x] = lines[x] + tuple([log.document])

    return render(
        request,
        'documents/logs.html',
        {'headers': headers, 'content': lines}
    )
